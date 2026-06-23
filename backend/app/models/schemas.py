from pydantic import BaseModel
from typing import List, Optional

class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks: int
    created_at: str
    file_type: str
    chunks_created: int
    message: str

class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    chunks: int
    created_at: str
    file_type: str

class CitedChunk(BaseModel):
    content: str
    source: str
    page: Optional[int]
    similarity_score: float

class QueryRequest(BaseModel):
    question: str
    doc_ids: Optional[List[str]] = None  # None = search all documents
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    cited_chunks: List[CitedChunk]
    confidence_score: float
    confidence_label: str

class CompareRequest(BaseModel):
    question: str
    doc_id_1: str
    doc_id_2: str

class CompareResponse(BaseModel):
    doc1_answer: str
    doc2_answer: str
    synthesis: str
    doc1_name: str
    doc2_name: str
