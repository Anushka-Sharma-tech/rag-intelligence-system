from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.ingestion import ingest_file, ingest_url, delete_document, get_all_documents
from app.models.schemas import DocumentUploadResponse, DocumentInfo

router = APIRouter(prefix="/documents", tags=["Documents"])

CONTENT_TYPE_MAP = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
}

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in CONTENT_TYPE_MAP:
        raise HTTPException(400, "Only PDF and DOCX files are supported")
    file_bytes = await file.read()
    doc_id, n_chunks = await ingest_file(file_bytes, file.filename, CONTENT_TYPE_MAP[file.content_type])
    return DocumentUploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        chunks_created=n_chunks,
        message=f"Processed '{file.filename}' → {n_chunks} chunks stored"
    )

@router.post("/upload-url", response_model=DocumentUploadResponse)
async def upload_url(url: str = Form(...)):
    try:
        doc_id, n_chunks = await ingest_url(url)
        return DocumentUploadResponse(
            doc_id=doc_id,
            filename=url,
            chunks_created=n_chunks,
            message=f"Processed URL → {n_chunks} chunks stored"
        )
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/", response_model=list[DocumentInfo])
async def list_documents():
    return [DocumentInfo(**d) for d in get_all_documents()]

@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    if not delete_document(doc_id):
        raise HTTPException(404, f"Document '{doc_id}' not found")
    return {"message": f"Document {doc_id} deleted"}