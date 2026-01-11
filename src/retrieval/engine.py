from typing import List, Dict
from src.retrieval.indexer import LegalIndexer

class RetrievalEngine:
    def __init__(self, persist_dir: str = "data/chroma_db"):
        self.indexer = LegalIndexer(persist_directory=persist_dir)
        self.collection = self.indexer.collection

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Semantic search for relevant legal sections.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )

        # Chroma returns lists of lists (one per query)
        # We assume single query
        hits = []
        if results["ids"]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            
            for i, doc_id in enumerate(ids):
                hits.append({
                    "id": doc_id,
                    "content": docs[i],
                    "metadata": metas[i]
                })
        
        return hits
