from storage.vector_store_manager import get_pdf_store, get_github_store

from rag.hybrid_search import HybridRetriever
from rag.reranker import rerank

from storage.vector_store_manager import (
    get_pdf_chunks,
    get_github_chunks
)


def retrieve_all(query, top_k=5):

    all_results = []

    # -------- PDF --------
    pdf_store = get_pdf_store()

    if pdf_store:

        pdf_chunks = get_pdf_chunks()

        pdf_retriever = HybridRetriever(
            pdf_store,
            pdf_chunks
        )

        pdf_results = pdf_retriever.retrieve(
            query,
            top_k
        )

        all_results.extend(pdf_results)

    # -------- GitHub --------
    github_store = get_github_store()

    if github_store:

        github_chunks = get_github_chunks()

        github_retriever = HybridRetriever(
            github_store,
            github_chunks
        )

        github_results = github_retriever.retrieve(
            query,
            top_k
        )

        all_results.extend(github_results)

    # -------- Final Reranking --------

    final_results = rerank(
        query,
        all_results,
        top_k=top_k
    )

    return final_results