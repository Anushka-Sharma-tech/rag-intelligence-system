from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, query
import os

app = FastAPI(
    title="RAG Intelligence API",
    description="Multi-document RAG with citations, similarity scores, and comparison mode",
    version="1.0.0"
)

frontend_origin = os.getenv("FRONTEND_ORIGIN")
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if frontend_origin:
    allowed_origins.append(frontend_origin.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.up\.railway\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(query.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
