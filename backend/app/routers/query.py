from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse, CompareRequest, CompareResponse
from app.services.rag import query_documents, compare_documents

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("/", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        return query_documents(request.question, request.doc_ids, request.top_k)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/compare", response_model=CompareResponse)
async def compare(request: CompareRequest):
    try:
        return compare_documents(request.question, request.doc_id_1, request.doc_id_2)
    except Exception as e:
        raise HTTPException(500, str(e))