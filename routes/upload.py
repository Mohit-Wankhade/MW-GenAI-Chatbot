import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from auth.auth_dependencies import get_current_user
from config import MAX_UPLOAD_SIZE_MB, PDF_INDEX_PATH, UPLOAD_FOLDER
from rag.embed import embedding_model
from rag.index_manager import create_or_update_index
from storage.chunk_manager import append_pdf_chunks
from storage.vector_store_manager import set_pdf_chunks, set_pdf_store
from utils.chunker_metadata import chunk_pages
from utils.logger import logger
from utils.monitoring import PDF_UPLOADS
from utils.pdf_loader_metadata import extract_pages_from_pdf


router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


_FILENAME_SAFE_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_filename(filename: str) -> str:
    original_name = Path(filename or "document.pdf").name
    safe_name = _FILENAME_SAFE_PATTERN.sub("_", original_name).strip("._")

    if not safe_name:
        safe_name = "document.pdf"

    return safe_name


def _validate_pdf_filename(filename: str) -> None:
    if not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )


async def _save_upload_file(
    file: UploadFile,
    destination: Path,
    max_size_mb: int,
) -> int:
    """
    Saves file in chunks and enforces upload size limit.
    """

    destination.parent.mkdir(parents=True, exist_ok=True)

    max_bytes = max_size_mb * 1024 * 1024
    total_bytes = 0

    try:
        with destination.open("wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"PDF is too large. Maximum allowed size is {max_size_mb} MB.",
                    )

                buffer.write(chunk)

    finally:
        await file.close()

    return total_bytes


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    _validate_pdf_filename(file.filename)

    safe_original_filename = _sanitize_filename(file.filename)

    stored_filename = f"{uuid4().hex}_{safe_original_filename}"
    file_path = Path(UPLOAD_FOLDER) / stored_filename

    try:
        size_bytes = await _save_upload_file(
            file=file,
            destination=file_path,
            max_size_mb=MAX_UPLOAD_SIZE_MB,
        )

        logger.info(
            "Uploaded PDF. user=%s original=%s stored=%s size_bytes=%s",
            current_user,
            safe_original_filename,
            stored_filename,
            size_bytes,
        )

        pages = extract_pages_from_pdf(
            pdf_path=str(file_path),
            source_name=stored_filename,
            original_filename=safe_original_filename,
            uploaded_by=current_user,
        )

        if not pages:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="PDF does not contain readable text.",
            )

        chunks = chunk_pages(
            pages=pages,
            source_name=stored_filename,
            original_filename=safe_original_filename,
            uploaded_by=current_user,
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No searchable chunks could be created from this PDF.",
            )

        logger.info(
            "Created PDF chunks. file=%s pages=%s chunks=%s",
            stored_filename,
            len(pages),
            len(chunks),
        )

        vector_store = create_or_update_index(
            chunks=chunks,
            embedding_model=embedding_model,
            index_path=PDF_INDEX_PATH,
        )

        all_pdf_chunks = append_pdf_chunks(chunks)

        set_pdf_store(vector_store)
        set_pdf_chunks(all_pdf_chunks)

        PDF_UPLOADS.inc()

        logger.info(
            "PDF indexed successfully. file=%s total_pdf_chunks=%s",
            stored_filename,
            len(all_pdf_chunks),
        )

        return {
            "message": "PDF indexed successfully.",
            "file": safe_original_filename,
            "stored_file": stored_filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "total_pdf_chunks": len(all_pdf_chunks),
            "size_bytes": size_bytes,
        }

    except HTTPException:
        if file_path.exists() and file_path.stat().st_size == 0:
            file_path.unlink(missing_ok=True)

        raise

    except Exception:
        logger.exception("PDF indexing failed. file=%s", safe_original_filename)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload and index PDF.",
        )