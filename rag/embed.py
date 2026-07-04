from functools import lru_cache
from typing import Iterable, List

from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL_NAME
from utils.logger import logger


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Loads the embedding model once and reuses it.

    Normalized embeddings generally improve cosine-similarity based retrieval.
    """

    logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


# Backward-compatible global variable.
embedding_model = get_embedding_model()


def get_embedding(texts: Iterable[str]) -> List[List[float]]:
    """
    Embeds a list of texts.

    Kept compatible with your existing imports.
    """

    clean_texts = [
        str(text or "").strip()
        for text in texts
        if str(text or "").strip()
    ]

    if not clean_texts:
        return []

    return embedding_model.embed_documents(clean_texts)


def get_query_embedding(text: str) -> List[float]:
    """
    Embeds a single query.

    Useful for future custom retrieval logic.
    """

    clean_text = str(text or "").strip()

    if not clean_text:
        return []

    return embedding_model.embed_query(clean_text)