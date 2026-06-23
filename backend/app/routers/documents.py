from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import DocumentInfo, DocumentUploadResponse
from app.services.ingestion import delete_document, get_all_documents, ingest_file, ingest_url

router = APIRouter(prefix="/documents", tags=["Documents"])

CONTENT_TYPE_MAP = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in CONTENT_TYPE_MAP:
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    file_type = CONTENT_TYPE_MAP[file.content_type]
    file_bytes = await file.read()
    doc_id, n_chunks, doc_info = await ingest_file(file_bytes, file.filename, file_type)

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
async def upload_url(url: str = Form(...)):
    try:
        doc_id, n_chunks, doc_info = await ingest_url(url)
        return DocumentUploadResponse(
            doc_id=doc_id,
            filename=doc_info["filename"],
            chunks=doc_info["chunks"],
            created_at=doc_info["created_at"],
            file_type=doc_info["file_type"],
            chunks_created=n_chunks,
            message=f"Processed URL -> {n_chunks} chunks stored",
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
