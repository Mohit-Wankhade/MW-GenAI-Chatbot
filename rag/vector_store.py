from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document



def search_vector_store(vector_store, query, top_k=3):
    docs= vector_store.similarity_search(query, k=top_k)
    return docs

def create_vector_store_with_metadata(chunks, embedding_model):
    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
        )

    return FAISS.from_documents(documents, embedding_model)

def create_code_vector_store(chunks, embedding_model):
    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["content"],
                metadata=chunk["metadata"]
            )
        )

    return FAISS.from_documents(documents, embedding_model)
   
