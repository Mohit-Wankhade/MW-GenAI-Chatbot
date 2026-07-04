import hashlib
from typing import Any, Dict, List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE


def _chunk_id(
    source_name: str,
    page_number: int,
    chunk_index: int,
    content: str,
) -> str:
    raw = f"{source_name}|{page_number}|{chunk_index}|{content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _clean_text(text: str) -> str:
    return " ".join(str(text or "").replace("\x00", " ").split())


def chunk_pages(
    pages: List[Dict[str, Any]],
    source_name: str,
    original_filename: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Splits extracted PDF pages into metadata-rich chunks.

    Output format:
    {
        "content": "...",
        "metadata": {
            "type": "pdf",
            "source": "stored-file.pdf",
            "original_filename": "resume.pdf",
            "page": 1,
            "chunk_index": 0,
            "chunk_id": "...",
            "uploaded_by": "username"
        }
    }
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ],
    )

    chunks: List[Dict[str, Any]] = []
    seen = set()

    for page in pages or []:
        page_text = _clean_text(page.get("text", ""))

        if not page_text:
            continue

        page_number = int(page.get("page_number", 0) or 0)

        split_chunks = splitter.split_text(page_text)

        for index, chunk in enumerate(split_chunks):
            clean_chunk = _clean_text(chunk)

            if not clean_chunk:
                continue

            chunk_hash = _chunk_id(
                source_name=source_name,
                page_number=page_number,
                chunk_index=index,
                content=clean_chunk,
            )

            if chunk_hash in seen:
                continue

            seen.add(chunk_hash)

            chunks.append(
                {
                    "content": clean_chunk,
                    "metadata": {
                        "type": "pdf",
                        "source": source_name,
                        "original_filename": original_filename
                        or page.get("original_filename")
                        or source_name,
                        "page": page_number,
                        "chunk_index": index,
                        "chunk_id": chunk_hash,
                        "uploaded_by": uploaded_by or page.get("uploaded_by"),
                    },
                }
            )

    return chunks