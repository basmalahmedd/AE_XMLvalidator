import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

class RagRetriever:
    def __init__(self, db_path="./chroma_db", collection_name="ae_schema"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(collection_name)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def _keyword_filter(self, query: str):
        keywords = []
        q = query.lower()
        if "cluster" in q:
            keywords.append("AeCpuCluster")
        if "chiplet" in q or "gpu" in q or "npu" in q:
            keywords.append("AeChipletType")
        if "network" in q:
            keywords.append("AeNetworkTopologyType")
        return keywords or ["AeCpuCluster", "AeChipletType"]

    def retrieve(self, query: str, top_k: int = 8):
        """Retrieve schema context most relevant to the user query."""
        keywords = self._keyword_filter(query)
        query_embed = self.model.encode(query)
        results = self.collection.query(
            query_embeddings=[query_embed.tolist()],
            n_results=top_k,
        )

        # Filter results for relevant schema types
        docs = results["documents"][0]
        filtered = [d for d in docs if any(k in d for k in keywords)]
        if not filtered:
            filtered = docs

        # Compact summary to make prompt concise
        context = "\n---\n".join(filtered[:5])
        return f"Relevant schema snippets ({', '.join(keywords)}):\n{context}"
