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
        # Using utf-8 handling to prevent errors with diverse file names
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_metadata(data: dict):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


async def ingest_file(file_bytes: bytes, filename: str, file_type: str, tenant: dict) -> Tuple[str, int, dict]:
    """
    Upgraded to accept a tenant dict containing identity profiles.
    """
    doc_id = str(uuid.uuid4())[:8]
    
    if file_type == "pdf":
        pages = extract_from_pdf(file_bytes, filename)
    elif file_type == "docx":
        pages = extract_from_docx(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported type: {file_type}")

    chunks = chunk_documents(pages, settings.chunk_size, settings.chunk_overlap)
    
    # Stop the process if the document had no readable text
    if not chunks:
        raise HTTPException(
            status_code=400, 
            detail="No readable text could be extracted. If this is a scanned PDF or image-based document, try uploading a standard text document."
        )

    # 🛑 THE SECURITY ADDITION: Inject the owner_id directly into each text chunk's metadata
    # This guarantees ChromaDB can filter search results natively by owner
    for chunk in chunks:
        if "metadata" not in chunk or chunk["metadata"] is None:
            chunk["metadata"] = {}
        chunk["metadata"]["owner_id"] = tenant["id"]

    embeddings = create_embeddings([c["text"] for c in chunks])
    
    # If your vector_store.add_document accepts a structural parameter for where filtering,
    # we pass it down here, or it reads it directly from the updated chunks above.
    # Inside ingestion.py (Both in ingest_file and ingest_url):
    vector_store.add_document(doc_id, chunks, embeddings, tenant_id=tenant["id"])

    # 🛑 THE METADATA ADDITION: Anchor owner properties into your JSON storage inventory
    doc_info = {
        "filename": filename,
        "file_type": file_type,
        "chunks": len(chunks),
        "created_at": datetime.now().isoformat(),
        "owner_id": tenant["id"],
        "is_guest": tenant["type"] == "guest"
    }
    
    metadata = _load_metadata()
    metadata[doc_id] = doc_info
    _save_metadata(metadata)
    
    return doc_id, len(chunks), doc_info


async def ingest_url(url: str, tenant: dict) -> Tuple[str, int, dict]:
    """
    Upgraded to link URL scrapes to their matching user session.
    """
    doc_id = str(uuid.uuid4())[:8]
    pages = extract_from_url(url)

    chunks = chunk_documents(pages, settings.chunk_size, settings.chunk_overlap)
    
    if not chunks:
        raise HTTPException(
            status_code=400, 
            detail="No readable text could be extracted from this URL. The website might be protected, an image, or empty."
        )

    # 🛑 THE SECURITY ADDITION: Tag every URL chunk with its owner ID
    for chunk in chunks:
        if "metadata" not in chunk or chunk["metadata"] is None:
            chunk["metadata"] = {}
        chunk["metadata"]["owner_id"] = tenant["id"]

    embeddings = create_embeddings([c["text"] for c in chunks])
    # Inside ingestion.py (Both in ingest_file and ingest_url):
    vector_store.add_document(doc_id, chunks, embeddings, tenant_id=tenant["id"])
    # 🛑 THE METADATA ADDITION: Save user ownership for URL logs
    doc_info = {
        "filename": url,
        "file_type": "url",
        "chunks": len(chunks),
        "created_at": datetime.now().isoformat(),
        "owner_id": tenant["id"],
        "is_guest": tenant["type"] == "guest"
    }
    
    metadata = _load_metadata()
    metadata[doc_id] = doc_info
    _save_metadata(metadata)
    
    return doc_id, len(chunks), doc_info


def delete_document(doc_id: str, tenant_id: str) -> bool:
    """
    Upgraded to prevent users from malicious or accidental cross-deletion targets.
    """
    metadata = _load_metadata()
    if doc_id not in metadata:
        return False
        
    # 🛑 COLD STOP: Block removal if the requester doesn't own this specific file record
    if metadata[doc_id].get("owner_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Permission denied. You do not own this document.")
        
    vector_store.delete_document(doc_id)
    del metadata[doc_id]
    _save_metadata(metadata)
    return True


def get_all_documents(tenant_id: str) -> list:
    """
    Upgraded to isolate file indexes. Users will only see their own workspace history.
    """
    metadata = _load_metadata()
    # 🛑 FILTER FILTER: Iterate through the inventory and only yield items matching the active ID
    return [
        {"doc_id": k, **v} 
        for k, v in metadata.items() 
        if v.get("owner_id") == tenant_id
    ]