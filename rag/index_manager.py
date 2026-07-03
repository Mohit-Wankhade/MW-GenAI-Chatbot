import os

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


def create_or_update_index(chunks, embedding_model, index_path):
    """
    Create a new FAISS index if none exists.
    Otherwise append new documents to the existing index.
    """

    existing_store = load_vector_store(embedding_model, index_path)

    documents = [
        Document(
            page_content=chunk["content"],
            metadata=chunk["metadata"]
        )
        for chunk in chunks
    ]

    if existing_store is not None:
        existing_store.add_documents(documents)
        save_vector_store(existing_store, index_path)
        return existing_store

    vector_store = FAISS.from_documents(
        documents,
        embedding_model
    )

    save_vector_store(vector_store, index_path)

    return vector_store


def save_vector_store(vector_store, index_path):

    os.makedirs(index_path, exist_ok=True)

    vector_store.save_local(index_path)


def load_vector_store(embedding_model, index_path):

    faiss_file = os.path.join(index_path, "index.faiss")
    pkl_file = os.path.join(index_path, "index.pkl")

    if not os.path.exists(faiss_file):
        return None

    if not os.path.exists(pkl_file):
        return None

    return FAISS.load_local(
        index_path,
        embedding_model,
        allow_dangerous_deserialization=True
    )