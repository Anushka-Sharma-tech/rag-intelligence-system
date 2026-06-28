import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import documents, query
from app.services.vectorstore import vector_store

METADATA_FILE = "./docs_metadata.json"


async def guest_data_garbage_collector():
    """
    Background worker that runs indefinitely. Wakes up once per hour to find 
    and completely erase guest user documents older than 2 hours.
    """
    while True:
        try:
            # Wake up every 3600 seconds (1 hour)
            await asyncio.sleep(3600)
            
            path = Path(METADATA_FILE)
            if not path.exists():
                continue

            with open(path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            updated_metadata = {}
            any_deleted = False

            for doc_id, info in metadata.items():
                is_guest = info.get("is_guest", False)
                created_at_str = info.get("created_at")
                owner_id = info.get("owner_id")

                should_delete = False
                if is_guest and created_at_str and owner_id:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                        # Check if the file age exceeds 2 hours (7200 seconds)
                        if (datetime.now() - created_at).total_seconds() > 7200:
                            should_delete = True
                    except Exception:
                        pass

                if should_delete:
                    # 1. Purge matching metadata vectors from ChromaDB
                    try:
                        vector_store.collection.delete(
                            where={
                                "$and": [
                                    {"doc_id": doc_id},
                                    {"owner_id": owner_id}
                                ]
                            }
                        )
                        any_deleted = True
                    except Exception as e:
                        print(f"GC Alert: Failed to purge vector space for {doc_id}: {e}")
                else:
                    # Keep records that aren't old guest instances
                    updated_metadata[doc_id] = info

            # 2. Re-write the catalog manifest file if changes occurred
            if any_deleted:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(updated_metadata, f, indent=2)
                print("GC Status: Successfully cleaned up expired guest session records.")

        except Exception as log_error:
            print(f"GC Core Exception caught: {log_error}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application startup and shutdown execution lifecycles.
    """
    # Startup: Initialize and start our automated cleaner routine
    gc_task = asyncio.create_task(guest_data_garbage_collector())
    yield
    # Shutdown: Safely stop the background worker task
    gc_task.cancel()


app = FastAPI(
    title="RAG Intelligence API",
    description="Multi-document RAG with citations, similarity scores, and comparison mode",
    version="1.0.0",
    lifespan=lifespan  # 🛑 Registers our new lifespan processor
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
    allow_headers=["*"],  # Allows custom headers like Authorization and X-Session-ID
)

# Include your app endpoints
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}