from typing import Any, Dict, List, Optional, Tuple

from rag.bm25_search import BM25Retriever
from rag.vector_store import search_vector_store


class HybridRetriever:
    """
    Combines dense vector search and sparse BM25 search.

    Uses simple Reciprocal Rank Fusion style scoring instead of just appending
    dense + sparse results. This improves ranking quality and avoids duplicates.
    """

    def __init__(
        self,
        vector_store: Any,
        chunks: List[Dict[str, Any]],
        rrf_k: int = 60,
    ):
        self.vector_store = vector_store
        self.chunks = chunks or []
        self.rrf_k = rrf_k
        self.bm25 = BM25Retriever(self.chunks)

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(str(text or "").lower().split())

    @staticmethod
    def _doc_key(content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        metadata = metadata or {}

        source = (
            metadata.get("source")
            or metadata.get("repo")
            or metadata.get("file")
            or metadata.get("path")
            or ""
        )

        return f"{source}|{HybridRetriever._normalize_text(content)[:500]}"

    @staticmethod
    def _from_langchain_doc(doc: Any) -> Dict[str, Any]:
        return {
            "content": getattr(doc, "page_content", ""),
            "metadata": getattr(doc, "metadata", {}) or {},
        }

    @staticmethod
    def _from_bm25_result(result: Any) -> Dict[str, Any]:
        """
        Supports common BM25 result formats:
        - (score, doc)
        - doc
        """

        if isinstance(result, tuple) and len(result) == 2:
            _, doc = result
        else:
            doc = result

        if isinstance(doc, dict):
            return {
                "content": doc.get("content", ""),
                "metadata": doc.get("metadata", {}) or {},
            }

        return {
            "content": getattr(doc, "page_content", str(doc)),
            "metadata": getattr(doc, "metadata", {}) or {},
        }

    def _add_result(
        self,
        fused_results: Dict[str, Dict[str, Any]],
        doc: Dict[str, Any],
        rank: int,
        source: str,
    ) -> None:
        content = str(doc.get("content", "")).strip()
        metadata = doc.get("metadata", {}) or {}

        if not content:
            return

        key = self._doc_key(content, metadata)
        score = 1.0 / (self.rrf_k + rank)

        if key not in fused_results:
            fused_results[key] = {
                "content": content,
                "metadata": metadata,
                "score": 0.0,
                "retrieval_sources": [],
            }

        fused_results[key]["score"] += score

        if source not in fused_results[key]["retrieval_sources"]:
            fused_results[key]["retrieval_sources"].append(source)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        dense_top_k: Optional[int] = None,
        sparse_top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        clean_query = " ".join(str(query or "").strip().split())

        if not clean_query:
            return []

        dense_k = dense_top_k or max(top_k, 5)
        sparse_k = sparse_top_k or max(top_k, 5)

        fused_results: Dict[str, Dict[str, Any]] = {}

        try:
            dense_docs = search_vector_store(
                self.vector_store,
                clean_query,
                dense_k,
            )

            for rank, doc in enumerate(dense_docs, start=1):
                self._add_result(
                    fused_results=fused_results,
                    doc=self._from_langchain_doc(doc),
                    rank=rank,
                    source="dense",
                )

        except Exception:
            # Let BM25 still work even if FAISS/vector search fails.
            dense_docs = []

        try:
            sparse_docs = self.bm25.search(
                clean_query,
                sparse_k,
            )

            for rank, result in enumerate(sparse_docs, start=1):
                self._add_result(
                    fused_results=fused_results,
                    doc=self._from_bm25_result(result),
                    rank=rank,
                    source="bm25",
                )

        except Exception:
            sparse_docs = []

        ranked_results = sorted(
            fused_results.values(),
            key=lambda item: item.get("score", 0.0),
            reverse=True,
        )

        return ranked_results[:top_k]