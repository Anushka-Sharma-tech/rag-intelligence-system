from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, query
import os

app = FastAPI(
    title="RAG Intelligence API",
    description="Multi-document RAG with citations, similarity scores, and comparison mode",
    version="1.0.0"
)

# 1. Exact origins allowed to talk to the backend
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://rag-intelligence-system.vercel.app"  # Your exact live Vercel domain
]

# 2. Dynamic backup check (if you ever set FRONTEND_ORIGIN in Railway Variables)
frontend_origin = os.getenv("FRONTEND_ORIGIN")
if frontend_origin:
    allowed_origins.append(frontend_origin.rstrip("/"))

# 3. Apply the bulletproof CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Safely allows all Vercel branch previews AND Railway internal domains
    allow_origin_regex=r"https://(.*\.vercel\.app|.*\.up\.railway\.app)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your app endpoints
app.include_router(documents.router)
app.include_router(query.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}