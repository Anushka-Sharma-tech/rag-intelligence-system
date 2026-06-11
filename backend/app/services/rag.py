from openai import OpenAI
from typing import List, Optional
from app.config import settings
from app.services.vectorstore import vector_store
from app.services.embeddings import create_query_embedding
from app.services.scoring import calculate_confidence, distance_to_similarity
from app.models.schemas import QueryResponse, CitedChunk, CompareResponse

# 🚀 SENIOR FIX: Pull the keys directly from your secured Pydantic settings
client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

def build_rag_prompt(question: str, chunks: List[str], metadatas: List[dict], distances: List[float]) -> str:
    """Build the prompt that gets sent to the LLM with retrieved context."""
    context_blocks = []
    for i, (chunk, meta, dist) in enumerate(zip(chunks, metadatas, distances)):
        sim = distance_to_similarity(dist)
        source = meta.get("source", "Unknown")
        page = meta.get("page", "")
        page_info = f" | Page {page}" if page else ""
        context_blocks.append(
            f"[Source {i+1}: {source}{page_info} | Similarity: {sim:.3f}]\n{chunk}"
        )
    context = "\n\n---\n\n".join(context_blocks)
    return f"""You are a precise document analysis assistant. Answer ONLY using the provided context.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Use ONLY information from the provided context
- Reference sources using [Source N] notation
- If the context lacks sufficient information, say so explicitly
- Be precise and concise

ANSWER:"""

def query_documents(
    question: str,
    doc_ids: Optional[List[str]] = None,
    top_k: int = 5
) -> QueryResponse:
    """Core RAG function: embed question → retrieve chunks → generate answer."""
    query_embedding = create_query_embedding(question)
    results = vector_store.query(query_embedding, top_k=top_k, doc_ids=doc_ids)
    
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    if not chunks:
        return QueryResponse(
            answer="No relevant content found. Please upload documents first.",
            cited_chunks=[],
            confidence_score=0.0,
            confidence_label="Low"
        )
        
    prompt = build_rag_prompt(question, chunks, metadatas, distances)
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,   # Low temp = factual, deterministic answers
        max_tokens=1200
    )
    
    answer = response.choices[0].message.content
    cited_chunks = [
        CitedChunk(
            content=chunk[:300] + "..." if len(chunk) > 300 else chunk,
            source=meta.get("source", "Unknown"),
            page=int(meta["page"]) if meta.get("page") and meta["page"].isdigit() else None,
            similarity_score=distance_to_similarity(dist)
        )
        for chunk, meta, dist in zip(chunks, metadatas, distances)
    ]
    
    confidence_score, confidence_label = calculate_confidence(distances)
    return QueryResponse(
        answer=answer,
        cited_chunks=cited_chunks,
        confidence_score=confidence_score,
        confidence_label=confidence_label
    )

def _get_single_doc_answer(question: str, doc_id: str) -> tuple[str, str]:
    """Helper: get answer for one doc and its name."""
    embedding = create_query_embedding(question)
    results = vector_store.query(embedding, top_k=3, doc_ids=[doc_id])
    
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    if not chunks:
        return "No relevant content found in this document.", doc_id
        
    prompt = build_rag_prompt(question, chunks, metadatas, distances)
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=600
    )
    source_name = metadatas[0].get("source", doc_id) if metadatas else doc_id
    return response.choices[0].message.content, source_name

def compare_documents(question: str, doc_id_1: str, doc_id_2: str) -> CompareResponse:
    """Answer the same question from two docs and synthesize the difference."""
    answer1, name1 = _get_single_doc_answer(question, doc_id_1)
    answer2, name2 = _get_single_doc_answer(question, doc_id_2)
    
    synthesis_prompt = f"""Two documents answered this question: "{question}"

Document 1 ({name1}): {answer1}
Document 2 ({name2}): {answer2}

In 3-4 sentences: what do they agree on, what differs, and which provides more detail?"""

    synthesis_response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": synthesis_prompt}],
        temperature=0.3,
        max_tokens=300
    )
    
    return CompareResponse(
        doc1_answer=answer1,
        doc2_answer=answer2,
        synthesis=synthesis_response.choices[0].message.content,
        doc1_name=name1,
        doc2_name=name2
    )