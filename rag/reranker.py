from functools import lru_cache
from typing import Any, Dict, List

from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL_NAME
from utils.logger import logger


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    """
    Loads the cross-encoder only once.

    This avoids reloading the reranker on every request and improves API latency.
    """

    logger.info("Loading reranker model: %s", RERANKER_MODEL_NAME)
    return CrossEncoder(RERANKER_MODEL_NAME)


def _get_content(document: Dict[str, Any]) -> str:
    return str(document.get("content", "")).strip()


def rerank(
    query: str,
    documents: List[Dict[str, Any]],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Reranks retrieved documents using a cross-encoder.

    Input document format:
    {
        "content": "...",
        "metadata": {...}
    }

    Output:
    Same document format, with an added "rerank_score".
    """

    clean_query = str(query or "").strip()

    if not clean_query or not documents:
        return []

    valid_documents = [
        doc for doc in documents
        if isinstance(doc, dict) and _get_content(doc)
    ]

    if not valid_documents:
        return []

    safe_top_k = max(1, min(top_k, len(valid_documents)))

    pairs = [
        (clean_query, _get_content(doc))
        for doc in valid_documents
    ]

    try:
        model = get_reranker()
        scores = model.predict(pairs)

        ranked = sorted(
            zip(scores, valid_documents),
            key=lambda item: float(item[0]),
            reverse=True,
        )

        results: List[Dict[str, Any]] = []

        for score, document in ranked[:safe_top_k]:
            enriched_document = document.copy()
            enriched_document["rerank_score"] = float(score)
            results.append(enriched_document)

        return results

    except Exception:
        logger.exception("Reranking failed. Returning original retrieval order.")
        return valid_documents[:safe_top_k]