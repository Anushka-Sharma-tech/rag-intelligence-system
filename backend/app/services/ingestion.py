from fastapi import HTTPException # Make sure this is at the top of ingestion.py!
import uuid
from typing import Tuple
from datetime import datetime
import json
from pathlib import Path


from app.config import settings
from app.services.embeddings import create_embeddings
from app.services.vectorstore import vector_store
from app.utils.chunker import chunk_documents
from app.utils.extractors import extract_from_docx, extract_from_pdf, extract_from_url

METADATA_FILE = "./docs_metadata.json"
ALLOWED_EXTENSIONS = {"pdf": "pdf", "docx": "docx"}


def _load_metadata() -> dict:
    if Path(METADATA_FILE).exists():
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_metadata(data: dict):
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def ingest_file(file_bytes: bytes, filename: str, file_type: str) -> Tuple[str, int, dict]:
    doc_id = str(uuid.uuid4())[:8]
    
    if file_type == "pdf":
        pages = extract_from_pdf(file_bytes, filename)
    elif file_type == "docx":
        pages = extract_from_docx(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported type: {file_type}")

    chunks = chunk_documents(pages, settings.chunk_size, settings.chunk_overlap)
    
    # 🛑 THE FIX: Stop the process if the document had no readable text
    if not chunks:
        raise HTTPException(
            status_code=400, 
            detail="No readable text could be extracted. If this is a scanned PDF or image-based document, try uploading a standard text document."
        )

    # If it passes the check, safely create embeddings and save!
    embeddings = create_embeddings([c["text"] for c in chunks])
    vector_store.add_document(doc_id, chunks, embeddings)

    doc_info = {
        "filename": filename,
        "file_type": file_type,
        "chunks": len(chunks),
        "created_at": datetime.now().isoformat(),
    }
    metadata = _load_metadata()
    metadata[doc_id] = doc_info
    _save_metadata(metadata)
    
    return doc_id, len(chunks), doc_info



async def ingest_url(url: str) -> Tuple[str, int, dict]:
    doc_id = str(uuid.uuid4())[:8]
    pages = extract_from_url(url)

    chunks = chunk_documents(pages, settings.chunk_size, settings.chunk_overlap)
    
    # 🛑 THE FIX: Add the exact same protection here!
    if not chunks:
        raise HTTPException(
            status_code=400, 
            detail="No readable text could be extracted from this URL. The website might be protected, an image, or empty."
        )

    embeddings = create_embeddings([c["text"] for c in chunks])
    vector_store.add_document(doc_id, chunks, embeddings)

    doc_info = {
        "filename": url,
        "file_type": "url",
        "chunks": len(chunks),
        "created_at": datetime.now().isoformat(),
    }
    metadata = _load_metadata()
    metadata[doc_id] = doc_info
    _save_metadata(metadata)
    
    return doc_id, len(chunks), doc_info

def delete_document(doc_id: str) -> bool:
    metadata = _load_metadata()
    if doc_id not in metadata:
        return False
    vector_store.delete_document(doc_id)
    del metadata[doc_id]
    _save_metadata(metadata)
    return True


def get_all_documents() -> list:
    metadata = _load_metadata()
    return [{"doc_id": k, **v} for k, v in metadata.items()]
