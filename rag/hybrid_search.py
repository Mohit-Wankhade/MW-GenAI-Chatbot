from rag.vector_store import search_vector_store
from rag.bm25_search import BM25Retriever

class HybridRetriever:
    def __init__(self, vector_store, chunks):
        self.vector_store = vector_store
        self.bm25= BM25Retriever(chunks)
        
    def retrieve(self, query, top_k=3):
        dense_docs= search_vector_store(self.vector_store, query, top_k)
        sparse_docs= self.bm25.search(query, top_k)
        results=[]
        seen=set()
        
        for doc in dense_docs:
            text= doc.page_content
            if text not in seen:
                seen.add(text)
                results.append({"content":text,"metadata": doc.metadata})
                
        for _, doc in sparse_docs:
            if doc["content"] not in seen:
                seen.add(doc["content"])
                results.append(doc)
        return results