import os
import pickle
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from config import GITHUB_CHUNK_PATH, PDF_CHUNK_PATH
from utils.logger import logger


Chunk = Dict[str, Any]


def _ensure_parent_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _chunk_key(chunk: Chunk) -> str:
    content = " ".join(str(chunk.get("content", "")).lower().split())
    metadata = chunk.get("metadata", {}) or {}

    source_identity = "|".join(
        str(metadata.get(field, ""))
        for field in ["type", "source", "original_filename", "repo", "file", "path", "page", "chunk_id"]
    )

    return f"{source_identity}|{content}"


def _deduplicate_chunks(chunks: List[Chunk]) -> List[Chunk]:
    deduped: List[Chunk] = []
    seen = set()

    for chunk in chunks or []:
        if not isinstance(chunk, dict):
            continue

        content = str(chunk.get("content", "")).strip()

        if not content:
            continue

        metadata = chunk.get("metadata", {})

        if not isinstance(metadata, dict):
            chunk["metadata"] = {}

        key = _chunk_key(chunk)

        if key in seen:
            continue

        seen.add(key)
        deduped.append(chunk)

    return deduped


def _atomic_pickle_save(data: Any, path: str) -> None:
    _ensure_parent_dir(path)

    target_path = Path(path)
    temp_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            delete=False,
            dir=str(target_path.parent),
            suffix=".tmp",
        ) as temp:
            temp_file = temp.name
            pickle.dump(data, temp)

        os.replace(temp_file, target_path)

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


def _load_chunks(path: str) -> List[Chunk]:
    if not os.path.exists(path):
        return []

    try:
        with open(path, "rb") as file:
            data = pickle.load(file)

        if not isinstance(data, list):
            logger.warning("Chunk file %s did not contain a list. Returning empty list.", path)
            return []

        return _deduplicate_chunks(data)

    except Exception:
        logger.exception("Failed to load chunks from %s.", path)
        return []


def _save_chunks(chunks: List[Chunk], path: str) -> List[Chunk]:
    clean_chunks = _deduplicate_chunks(chunks)
    _atomic_pickle_save(clean_chunks, path)

    logger.info("Saved %s chunks to %s.", len(clean_chunks), path)

    return clean_chunks


def _append_chunks(new_chunks: List[Chunk], path: str) -> List[Chunk]:
    existing_chunks = _load_chunks(path)
    merged_chunks = _deduplicate_chunks(existing_chunks + (new_chunks or []))

    _atomic_pickle_save(merged_chunks, path)

    logger.info(
        "Appended chunks to %s. existing=%s new=%s total=%s",
        path,
        len(existing_chunks),
        len(new_chunks or []),
        len(merged_chunks),
    )

    return merged_chunks


# ---------- PDF ----------

def save_pdf_chunks(chunks: List[Chunk]) -> List[Chunk]:
    """
    Replaces the PDF chunk file with provided chunks.

    Use append_pdf_chunks() after a new upload so older PDFs are not lost.
    """

    return _save_chunks(
        chunks=chunks,
        path=PDF_CHUNK_PATH,
    )


def append_pdf_chunks(chunks: List[Chunk]) -> List[Chunk]:
    """
    Appends new PDF chunks to the existing PDF chunk file with deduplication.

    This fixes the important bug where BM25 only searched the latest uploaded PDF.
    """

    return _append_chunks(
        new_chunks=chunks,
        path=PDF_CHUNK_PATH,
    )


def load_pdf_chunks() -> List[Chunk]:
    return _load_chunks(PDF_CHUNK_PATH)


# ---------- GitHub ----------

def save_github_chunks(chunks: List[Chunk]) -> List[Chunk]:
    """
    Replaces the GitHub chunk file with provided chunks.
    """

    return _save_chunks(
        chunks=chunks,
        path=GITHUB_CHUNK_PATH,
    )


def append_github_chunks(chunks: List[Chunk]) -> List[Chunk]:
    """
    Appends new GitHub chunks to the existing GitHub chunk file with deduplication.
    """

    return _append_chunks(
        new_chunks=chunks,
        path=GITHUB_CHUNK_PATH,
    )


def load_github_chunks() -> List[Chunk]:
    return _load_chunks(GITHUB_CHUNK_PATH)