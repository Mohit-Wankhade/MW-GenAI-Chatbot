from typing import Any, Dict, List, Optional

from config import BM25_TOP_K, HYBRID_TOP_K, RERANK_TOP_K, VECTOR_TOP_K
from rag.hybrid_search import HybridRetriever
from rag.reranker import rerank
from storage.vector_store_manager import (
    get_github_chunks,
    get_github_store,
    get_pdf_chunks,
    get_pdf_store,
)
from utils.logger import logger


def _safe_query(query: str) -> str:
    return " ".join(str(query or "").strip().split())


def _content_key(content: str) -> str:
    return " ".join(str(content or "").lower().split())


def _normalize_result(
    result: Dict[str, Any],
    source_type: str,
) -> Optional[Dict[str, Any]]:
    content = str(result.get("content", "")).strip()

    if not content:
        return None

    metadata = result.get("metadata", {}) or {}

    if not isinstance(metadata, dict):
        metadata = {}

    metadata.setdefault("type", source_type)

    return {
        "content": content,
        "metadata": metadata,
        "score": result.get("score"),
        "retrieval_sources": result.get("retrieval_sources", []),
    }


def _deduplicate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deduped: List[Dict[str, Any]] = []
    seen = set()

    for result in results:
        content = result.get("content", "")
        metadata = result.get("metadata", {}) or {}

        source_identity = (
            metadata.get("type"),
            metadata.get("source"),
            metadata.get("repo"),
            metadata.get("file"),
            metadata.get("page"),
        )

        key = (source_identity, _content_key(content)[:700])

        if key in seen:
            continue

        seen.add(key)
        deduped.append(result)

    return deduped


def _retrieve_from_store(
    query: str,
    vector_store: Any,
    chunks: List[Dict[str, Any]],
    source_type: str,
    top_k: int,
) -> List[Dict[str, Any]]:
    if vector_store is None:
        return []

    if not chunks:
        logger.warning("No chunks found for %s store. Skipping retrieval.", source_type)
        return []

    try:
        retriever = HybridRetriever(
            vector_store=vector_store,
            chunks=chunks,
        )

        raw_results = retriever.retrieve(
            query=query,
            top_k=max(top_k, HYBRID_TOP_K),
            dense_top_k=VECTOR_TOP_K,
            sparse_top_k=BM25_TOP_K,
        )

        normalized_results = []

        for result in raw_results:
            normalized = _normalize_result(
                result=result,
                source_type=source_type,
            )

            if normalized:
                normalized_results.append(normalized)

        logger.info(
            "Retrieved %s %s results.",
            len(normalized_results),
            source_type,
        )

        return normalized_results

    except Exception:
        logger.exception("Retrieval failed for %s store.", source_type)
        return []


def retrieve_all(
    query: str,
    top_k: int = RERANK_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Retrieves relevant chunks from both PDF and GitHub indexes.

    Pipeline:
    1. Hybrid retrieval from PDF index.
    2. Hybrid retrieval from GitHub index.
    3. Deduplication.
    4. Cross-encoder reranking.
    """

    clean_query = _safe_query(query)

    if not clean_query:
        return []

    safe_top_k = max(1, min(int(top_k or RERANK_TOP_K), 20))

    all_results: List[Dict[str, Any]] = []

    pdf_results = _retrieve_from_store(
        query=clean_query,
        vector_store=get_pdf_store(),
        chunks=get_pdf_chunks() or [],
        source_type="pdf",
        top_k=safe_top_k,
    )

    all_results.extend(pdf_results)

    github_results = _retrieve_from_store(
        query=clean_query,
        vector_store=get_github_store(),
        chunks=get_github_chunks() or [],
        source_type="github",
        top_k=safe_top_k,
    )

    all_results.extend(github_results)

    all_results = _deduplicate_results(all_results)

    if not all_results:
        logger.info("No retrieval results found for query.")
        return []

    final_results = rerank(
        query=clean_query,
        documents=all_results,
        top_k=safe_top_k,
    )

    logger.info(
        "Final reranked results: %s",
        len(final_results),
    )

    return final_results