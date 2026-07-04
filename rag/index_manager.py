import hashlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from utils.logger import logger


def _clean_content(content: Any) -> str:
    return str(content or "").strip()


def _clean_metadata(metadata: Any) -> Dict[str, Any]:
    if isinstance(metadata, dict):
        return metadata

    return {}


def _document_key(content: str, metadata: Dict[str, Any]) -> str:
    """
    Stable key used to reduce duplicate chunks during index updates.
    """

    source_identity = "|".join(
        str(metadata.get(field, ""))
        for field in ["type", "source", "repo", "file", "path", "page", "chunk_id"]
    )

    normalized_content = " ".join(content.lower().split())

    raw_key = f"{source_identity}|{normalized_content}"

    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def _chunk_to_document(chunk: Dict[str, Any]) -> Optional[Document]:
    content = _clean_content(chunk.get("content"))

    if not content:
        return None

    return Document(
        page_content=content,
        metadata=_clean_metadata(chunk.get("metadata")),
    )


def _chunks_to_documents(chunks: Iterable[Dict[str, Any]]) -> List[Document]:
    documents: List[Document] = []

    for chunk in chunks or []:
        if not isinstance(chunk, dict):
            continue

        document = _chunk_to_document(chunk)

        if document:
            documents.append(document)

    return documents


def _existing_document_keys(vector_store: FAISS) -> Set[str]:
    """
    Extracts keys from existing FAISS docstore to avoid adding exact duplicates.
    """

    keys: Set[str] = set()

    try:
        docstore_dict = getattr(vector_store.docstore, "_dict", {})

        for document in docstore_dict.values():
            if not isinstance(document, Document):
                continue

            content = _clean_content(document.page_content)
            metadata = _clean_metadata(document.metadata)

            if content:
                keys.add(_document_key(content, metadata))

    except Exception:
        logger.warning("Could not inspect existing FAISS documents for deduplication.")

    return keys


def _deduplicate_new_documents(
    documents: List[Document],
    existing_keys: Optional[Set[str]] = None,
) -> List[Document]:
    existing_keys = existing_keys or set()
    output: List[Document] = []
    seen = set(existing_keys)

    for document in documents:
        content = _clean_content(document.page_content)
        metadata = _clean_metadata(document.metadata)

        if not content:
            continue

        key = _document_key(content, metadata)

        if key in seen:
            continue

        seen.add(key)
        output.append(document)

    return output


def create_or_update_index(
    chunks: List[Dict[str, Any]],
    embedding_model: Any,
    index_path: str,
) -> Optional[FAISS]:
    """
    Creates a new FAISS index if none exists.
    Otherwise, appends only new non-duplicate documents to the existing index.
    """

    documents = _chunks_to_documents(chunks)

    if not documents:
        logger.warning("No valid chunks provided. Index was not created or updated.")
        return load_vector_store(
            embedding_model=embedding_model,
            index_path=index_path,
        )

    existing_store = load_vector_store(
        embedding_model=embedding_model,
        index_path=index_path,
    )

    if existing_store is not None:
        existing_keys = _existing_document_keys(existing_store)
        new_documents = _deduplicate_new_documents(
            documents=documents,
            existing_keys=existing_keys,
        )

        if not new_documents:
            logger.info("No new documents to add. Existing FAISS index unchanged.")
            return existing_store

        logger.info(
            "Adding %s new documents to existing FAISS index at %s.",
            len(new_documents),
            index_path,
        )

        existing_store.add_documents(new_documents)

        save_vector_store(
            vector_store=existing_store,
            index_path=index_path,
        )

        return existing_store

    unique_documents = _deduplicate_new_documents(documents)

    if not unique_documents:
        logger.warning("No unique documents found. FAISS index was not created.")
        return None

    logger.info(
        "Creating new FAISS index at %s with %s documents.",
        index_path,
        len(unique_documents),
    )

    vector_store = FAISS.from_documents(
        documents=unique_documents,
        embedding=embedding_model,
    )

    save_vector_store(
        vector_store=vector_store,
        index_path=index_path,
    )

    return vector_store


def save_vector_store(
    vector_store: FAISS,
    index_path: str,
) -> None:
    if vector_store is None:
        raise ValueError("vector_store cannot be None.")

    path = Path(index_path)
    path.mkdir(parents=True, exist_ok=True)

    vector_store.save_local(str(path))

    logger.info("FAISS index saved at %s.", path)


def load_vector_store(
    embedding_model: Any,
    index_path: str,
) -> Optional[FAISS]:
    path = Path(index_path)

    faiss_file = path / "index.faiss"
    pkl_file = path / "index.pkl"

    if not faiss_file.exists() or not pkl_file.exists():
        return None

    try:
        vector_store = FAISS.load_local(
            folder_path=str(path),
            embeddings=embedding_model,
            allow_dangerous_deserialization=True,
        )

        logger.info("FAISS index loaded from %s.", path)

        return vector_store

    except Exception:
        logger.exception("Failed to load FAISS index from %s.", path)
        return None