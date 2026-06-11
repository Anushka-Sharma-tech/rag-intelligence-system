from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, query

app = FastAPI(
    title="RAG Intelligence API",
    description="Multi-document RAG with citations, similarity scores, and comparison mode",
    version="1.0.0"
)

# Added both local variations to make it bulletproof
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(query.router)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}