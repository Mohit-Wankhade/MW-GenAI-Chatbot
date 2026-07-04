import re
from typing import Any, Dict, List, Tuple

from rank_bm25 import BM25Okapi


_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_./#:+-]+")


def tokenize(text: str) -> List[str]:
    """
    Better tokenization than simple .split().

    Keeps useful programming tokens like:
    - app.py
    - /chat-stream
    - jwt
    - faiss-cpu
    - user_id
    """

    return _TOKEN_PATTERN.findall(str(text or "").lower())


class BM25Retriever:
    def __init__(self, chunks: List[Dict[str, Any]]):
        self.documents = [
            chunk for chunk in chunks or []
            if isinstance(chunk, dict) and str(chunk.get("content", "")).strip()
        ]

        self.tokenized_corpus = [
            tokenize(chunk["content"])
            for chunk in self.documents
        ]

        self.bm25 = (
            BM25Okapi(self.tokenized_corpus)
            if self.tokenized_corpus
            else None
        )

    def search(
        self,
        query: str,
        k: int = 5,
        min_score: float = 0.0,
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Returns:
        [
            (score, {"content": "...", "metadata": {...}})
        ]
        """

        if self.bm25 is None or not self.documents:
            return []

        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        safe_k = max(1, min(int(k or 5), len(self.documents)))

        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            zip(scores, self.documents),
            reverse=True,
            key=lambda item: float(item[0]),
        )

        filtered_ranked = [
            (float(score), document)
            for score, document in ranked
            if float(score) > min_score
        ]

        return filtered_ranked[:safe_k]