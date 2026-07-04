from typing import Any, Dict, Iterable, List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from utils.logger import logger


def _clean_content(content: Any) -> str:
    return str(content or "").strip()


def _clean_metadata(metadata: Any) -> Dict[str, Any]:
    if isinstance(metadata, dict):
        return metadata

    return {}


def _chunk_to_document(chunk: Dict[str, Any]) -> Optional[Document]:
    content = _clean_content(chunk.get("content"))

    if not content:
        return None

    return Document(
        page_content=content,
        metadata=_clean_metadata(chunk.get("metadata")),
    )


def chunks_to_documents(chunks: Iterable[Dict[str, Any]]) -> List[Document]:
    documents: List[Document] = []

    for chunk in chunks or []:
        if not isinstance(chunk, dict):
            continue

        document = _chunk_to_document(chunk)

        if document:
            documents.append(document)

    return documents


def search_vector_store(
    vector_store: Any,
    query: str,
    top_k: int = 3,
) -> List[Document]:
    """
    Runs FAISS similarity search and returns LangChain Document objects.

    Kept compatible with HybridRetriever.
    """

    clean_query = str(query or "").strip()

    if vector_store is None or not clean_query:
        return []

    safe_top_k = max(1, min(int(top_k or 3), 50))

    try:
        return vector_store.similarity_search(
            clean_query,
            k=safe_top_k,
        )

    except Exception:
        logger.exception("Vector store similarity search failed.")
        return []


def search_vector_store_with_scores(
    vector_store: Any,
    query: str,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Optional helper for debugging and future ranking improvements.

    Returns:
    [
        {
            "content": "...",
            "metadata": {...},
            "distance": 0.123
        }
    ]
    """

    clean_query = str(query or "").strip()

    if vector_store is None or not clean_query:
        return []

    safe_top_k = max(1, min(int(top_k or 3), 50))

    try:
        results = vector_store.similarity_search_with_score(
            clean_query,
            k=safe_top_k,
        )

        formatted_results = []

        for document, score in results:
            formatted_results.append(
                {
                    "content": document.page_content,
                    "metadata": document.metadata or {},
                    "distance": float(score),
                }
            )

        return formatted_results

    except Exception:
        logger.exception("Vector store similarity search with scores failed.")
        return []


def create_vector_store_with_metadata(
    chunks: List[Dict[str, Any]],
    embedding_model: Any,
) -> Optional[FAISS]:
    """
    Creates a FAISS vector store from text chunks with metadata.
    """

    documents = chunks_to_documents(chunks)

    if not documents:
        logger.warning("No valid documents found. FAISS index was not created.")
        return None

    try:
        return FAISS.from_documents(
            documents=documents,
            embedding=embedding_model,
        )

    except Exception:
        logger.exception("Failed to create FAISS vector store.")
        raise


def create_code_vector_store(
    chunks: List[Dict[str, Any]],
    embedding_model: Any,
) -> Optional[FAISS]:
    """
    Creates a FAISS vector store for GitHub/code chunks.

    Kept separate for readability and backward compatibility, but internally it
    uses the same implementation as PDF chunks.
    """

    return create_vector_store_with_metadata(
        chunks=chunks,
        embedding_model=embedding_model,
    )