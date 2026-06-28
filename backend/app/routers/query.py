from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import QueryRequest, QueryResponse, CompareRequest, CompareResponse
from app.services.rag import query_documents, compare_documents
# 🛑 IMPORT the security bouncer
from app.services.auth import get_current_tenant

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    tenant: dict = Depends(get_current_tenant) # 🛑 FORCE identity checks here
):
    try:
        # Pass tenant["id"] down into your RAG query function so it can apply the 
        # ChromaDB where={"owner_id": tenant_id} filter internally.
        return query_documents(
            question=request.question, 
            doc_ids=request.doc_ids, 
            top_k=request.top_k,
            tenant_id=tenant["id"] # 🛑 Pass the owner lock down
        )
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/compare", response_model=CompareResponse)
async def compare(
    request: CompareRequest,
    tenant: dict = Depends(get_current_tenant) # 🛑 FORCE identity checks here
):
    try:
        # Pass tenant["id"] here as well to make sure they aren't trying to 
        # cross-compare documents belonging to other users.
        return compare_documents(
            question=request.question, 
            doc_id_1=request.doc_id_1, 
            doc_id_2=request.doc_id_2,
            tenant_id=tenant["id"] # 🛑 Pass the owner lock down
        )
    except Exception as e:
        raise HTTPException(500, str(e))