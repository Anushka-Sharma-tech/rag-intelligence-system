from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, query
import os

app = FastAPI(
    title="RAG Intelligence API",
    description="Multi-document RAG with citations, similarity scores, and comparison mode",
    version="1.0.0"
)

# 1. Initialize the list with your local development links
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# 2. Paste your live production Vercel URL right here (Make sure there is no trailing slash)
vercel_production_url = "https://your-actual-project.vercel.app"  # ← CHANGE THIS TO YOUR REAL VERCEL URL
allowed_origins.append(vercel_production_url.rstrip("/"))

# 3. Dynamic backup check (in case you set FRONTEND_ORIGIN in Railway variables)
frontend_origin = os.getenv("FRONTEND_ORIGIN")
if frontend_origin:
    allowed_origins.append(frontend_origin.rstrip("/"))

# 4. Apply a SINGLE clean middleware configuration block
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.up\.railway\.app",  # Allows Railway service domains to communicate
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