import chromadb
from typing import List, Dict, Optional
from app.config import settings

class VectorStore:
    """
    Wraps ChromaDB with cosine similarity.
    All documents share one collection; filtered by doc_id metadata.
    """
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_document(self, doc_id: str, chunks: List[Dict], embeddings: List[List[float]]) -> int:
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "doc_id": doc_id,
                "source": c["source"],
                "page": str(c.get("page") or ""),
                "chunk_index": str(c["chunk_index"])
            }
            for c in chunks
        ]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        return len(chunks)

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        doc_ids: Optional[List[str]] = None
    ) -> Dict:
        where = {"doc_id": {"$in": doc_ids}} if doc_ids else None
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

    def delete_document(self, doc_id: str):
        self.collection.delete(where={"doc_id": doc_id})

    def document_exists(self, doc_id: str) -> bool:
        results = self.collection.get(where={"doc_id": doc_id}, limit=1)
        return len(results["ids"]) > 0

# Singleton — import this everywhere
vector_store = VectorStore()