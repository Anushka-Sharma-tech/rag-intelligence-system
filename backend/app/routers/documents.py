from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends

from app.models.schemas import DocumentInfo, DocumentUploadResponse
from app.services.ingestion import delete_document, get_all_documents, ingest_file, ingest_url
# 🛑 IMPORT the security bouncer dependency
from app.services.auth import get_current_tenant

router = APIRouter(prefix="/documents", tags=["Documents"])

CONTENT_TYPE_MAP = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    tenant: dict = Depends(get_current_tenant) # 🛑 FORCE identity checks here
):
    if file.content_type not in CONTENT_TYPE_MAP:
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    file_type = CONTENT_TYPE_MAP[file.content_type]
    file_bytes = await file.read()
    
    # Pass down the tenant dictionary so metadata can lock ownership to this workspace partition
    doc_id, n_chunks, doc_info = await ingest_file(file_bytes, file.filename, file_type, tenant)

    return DocumentUploadResponse(
        doc_id=doc_id,
        filename=doc_info["filename"],
        chunks=doc_info["chunks"],
        created_at=doc_info["created_at"],
        file_type=doc_info["file_type"],
        chunks_created=n_chunks,
        message=f"Processed '{file.filename}' -> {n_chunks} chunks stored",
    )


@router.post("/upload-url", response_model=DocumentUploadResponse)
async def upload_url(
    url: str = Form(...),
    tenant: dict = Depends(get_current_tenant) # 🛑 FORCE identity checks here
):
    try:
        # Pass down the tenant dictionary to isolate scraped URLs to this session/user
        doc_id, n_chunks, doc_info = await ingest_url(url, tenant)
        return DocumentUploadResponse(
            doc_id=doc_id,
            filename=doc_info["filename"],
            chunks=doc_info["chunks"],
            created_at=doc_info["created_at"],
            file_type=doc_info["file_type"],
            chunks_created=n_chunks,
            message=f"Processed URL -> {n_chunks} chunks stored",
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/", response_model=list[DocumentInfo])
async def list_documents(
    tenant: dict = Depends(get_current_tenant) # 🛑 FORCE identity checks here
):
    # Only pull back files matching the active tenant's identity ID
    return [DocumentInfo(**d) for d in get_all_documents(tenant_id=tenant["id"])]


@router.delete("/{doc_id}")
async def remove_document(
    doc_id: str,
    tenant: dict = Depends(get_current_tenant) # 🛑 FORCE identity checks here
):
    # Pass both document ID and calling tenant ID to prevent cross-tenant deletion attacks
    if not delete_document(doc_id=doc_id, tenant_id=tenant["id"]):
        raise HTTPException(404, f"Document '{doc_id}' not found")
    return {"message": f"Document {doc_id} deleted"}