import chromadb
from typing import List, Dict, Optional
from app.config import settings

class VectorStore:
    """
    Wraps ChromaDB with cosine similarity.
    All documents share one collection; filtered strictly by tenant_id (owner_id) 
    and optional doc_id metadata to enforce structural multi-tenancy.
    """
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_document(self, doc_id: str, chunks: List[Dict], embeddings: List[List[float]], tenant_id: str) -> int:
        """
        Upgraded to accept a tenant_id and append it directly to ChromaDB's internal metadata.
        """
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "doc_id": doc_id,
                "owner_id": tenant_id,  # 🛑 THE LOCK: Tagging every chunk with the owner's session/Google ID
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
        tenant_id: str,  # 🛑 UPGRADE: Required tenant context parameter
        top_k: int = 5,
        doc_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Upgraded to enforce strict isolation boundaries on vector query matching.
        """
        # If the user selected specific documents to query against, enforce BOTH conditions
        if doc_ids:
            where = {
                "$and": [
                    {"owner_id": tenant_id},       # Must belong to this user
                    {"doc_id": {"$in": doc_ids}}   # Must match the specified documents
                ]
            }
        else:
            # If searching across their whole workspace, match anything owned by this tenant
            where = {"owner_id": tenant_id}

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

    def delete_document(self, doc_id: str, tenant_id: str):
        """
        Upgraded to prevent accidental or malicious cross-tenant file purges.
        """
        self.collection.delete(
            where={
                "$and": [
                    {"doc_id": doc_id},
                    {"owner_id": tenant_id}
                ]
            }
        )

    def document_exists(self, doc_id: str, tenant_id: str) -> bool:
        """
        Upgraded to verify existence exclusively within the scope of the requesting user.
        """
        results = self.collection.get(
            where={
                "$and": [
                    {"doc_id": doc_id},
                    {"owner_id": tenant_id}
                ]
            }, 
            limit=1
        )
        return len(results["ids"]) > 0

# Singleton — import this everywhere
vector_store = VectorStore()