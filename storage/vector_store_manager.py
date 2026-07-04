from threading import RLock
from typing import Any, Dict, List, Optional

from config import GITHUB_INDEX_PATH, PDF_INDEX_PATH
from rag.embed import embedding_model
from rag.index_manager import load_vector_store
from storage.chunk_manager import load_github_chunks, load_pdf_chunks
from utils.logger import logger


_cache_lock = RLock()

pdf_store = None
github_store = None

pdf_chunks: Optional[List[Dict[str, Any]]] = None
github_chunks: Optional[List[Dict[str, Any]]] = None


# ---------------- PDF Vector Store ----------------

def set_pdf_store(store: Any) -> None:
    global pdf_store

    with _cache_lock:
        pdf_store = store


def get_pdf_store() -> Any:
    global pdf_store

    with _cache_lock:
        if pdf_store is None:
            pdf_store = load_vector_store(
                embedding_model=embedding_model,
                index_path=PDF_INDEX_PATH,
            )

        return pdf_store


def refresh_pdf_store() -> Any:
    """
    Force reload PDF FAISS index from disk.
    Useful after upload/index update.
    """

    global pdf_store

    with _cache_lock:
        pdf_store = load_vector_store(
            embedding_model=embedding_model,
            index_path=PDF_INDEX_PATH,
        )

        return pdf_store


def clear_pdf_store() -> None:
    global pdf_store

    with _cache_lock:
        pdf_store = None


# ---------------- GitHub Vector Store ----------------

def set_github_store(store: Any) -> None:
    global github_store

    with _cache_lock:
        github_store = store


def get_github_store() -> Any:
    global github_store

    with _cache_lock:
        if github_store is None:
            github_store = load_vector_store(
                embedding_model=embedding_model,
                index_path=GITHUB_INDEX_PATH,
            )

        return github_store


def refresh_github_store() -> Any:
    """
    Force reload GitHub FAISS index from disk.
    Useful after GitHub repo indexing.
    """

    global github_store

    with _cache_lock:
        github_store = load_vector_store(
            embedding_model=embedding_model,
            index_path=GITHUB_INDEX_PATH,
        )

        return github_store


def clear_github_store() -> None:
    global github_store

    with _cache_lock:
        github_store = None


# ---------------- PDF Chunks ----------------

def set_pdf_chunks(chunks: List[Dict[str, Any]]) -> None:
    global pdf_chunks

    with _cache_lock:
        pdf_chunks = chunks or []


def get_pdf_chunks() -> List[Dict[str, Any]]:
    global pdf_chunks

    with _cache_lock:
        if pdf_chunks is None:
            pdf_chunks = load_pdf_chunks()

        return pdf_chunks or []


def refresh_pdf_chunks() -> List[Dict[str, Any]]:
    global pdf_chunks

    with _cache_lock:
        pdf_chunks = load_pdf_chunks()
        return pdf_chunks or []


def clear_pdf_chunks() -> None:
    global pdf_chunks

    with _cache_lock:
        pdf_chunks = None


# ---------------- GitHub Chunks ----------------

def set_github_chunks(chunks: List[Dict[str, Any]]) -> None:
    global github_chunks

    with _cache_lock:
        github_chunks = chunks or []


def get_github_chunks() -> List[Dict[str, Any]]:
    global github_chunks

    with _cache_lock:
        if github_chunks is None:
            github_chunks = load_github_chunks()

        return github_chunks or []


def refresh_github_chunks() -> List[Dict[str, Any]]:
    global github_chunks

    with _cache_lock:
        github_chunks = load_github_chunks()
        return github_chunks or []


def clear_github_chunks() -> None:
    global github_chunks

    with _cache_lock:
        github_chunks = None


# ---------------- Full Cache Reset ----------------

def clear_all_cached_stores() -> None:
    """
    Clears in-memory stores/chunks.

    Disk indexes and chunk files are not deleted.
    """

    clear_pdf_store()
    clear_github_store()
    clear_pdf_chunks()
    clear_github_chunks()

    logger.info("In-memory vector store and chunk caches cleared.")