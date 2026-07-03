from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, chunks):
        self.documents =chunks
        tokanized = [chunk["content"].lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokanized)
    
    def search(self, query, k=5):
        scores = self.bm25.get_scores(query.lower().split())
        ranked = sorted(zip(scores,self.documents), reverse=True, key=lambda x: x[0])
        return ranked[:k]
        