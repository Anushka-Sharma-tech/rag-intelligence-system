

---

# RAG Intelligence System

A modular, privacy-focused Retrieval-Augmented Generation (RAG) architecture designed for secure document intelligence. The system supports multi-tenant isolation, automated session management, and deterministic retrieval using local vectorization.

## Overview

This system enables ingestion, indexing, and synthesis of private documents. It separates the embedding layer from the generation layer, ensuring document data never leaves your infrastructure during vectorization. The architecture is built to handle both temporary guest sessions and permanent authenticated user workspaces.

## Tech Stack

| Category | Technology |
| --- | --- |
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **Orchestration** | Pydantic V2, Watchfiles |
| **Vector Engine** | ChromaDB, HuggingFace (`all-MiniLM-L6-v2`) |
| **LLM Inference** | Groq Cloud API (`openai/gpt-oss-20b`) |
| **Authentication** | Supabase Auth (Google OAuth) |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |

---

## Architectural Breakdown

### Backend Services (`/backend/app/services`)

The backend is structured to enforce security boundaries between unauthenticated guests and authenticated members.

* **`auth.py`**: Manages security context. Decodes Google JWTs for members and provisions/validates ephemeral session headers for guests.
* **`ingestion.py`**: Handles file processing. Tags every document chunk with a `tenant_id` to prevent cross-contamination in the vector store.
* **`vectorstore.py`**: The interface for ChromaDB. It enforces strict `tenant_id` filtering on all CRUD operations, ensuring users can only interact with their own data.
* **`rag.py`**: Orchestrates the retrieval pipeline. Filters retrieved chunks by session context before passing them to the LLM.
* **`main.py`**: Application entry point. Hosts the asynchronous garbage collector that prunes expired guest data every 60 minutes.

### Frontend (`/frontend/src`)

* **`lib/api.ts`**: Centralized API utility. Automatically detects auth state and injects either `Authorization` (Bearer token) or `X-Session-ID` (Guest) headers into all outbound requests.
* **`app/page.tsx`**: Primary dashboard interface. Manages state synchronization between Supabase auth cycles and the backend document inventory.

---

## Setup & Configuration

### Prerequisites

* Python 3.11+
* Node.js 18+
* Groq API Key
* Supabase Project URL & Anon Key

### Backend Initialization

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

```

Create a `.env` file in the `backend/` directory:

```env
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key

```

Start the service:

```bash
uvicorn app.main:app --reload

```

### Frontend Initialization

```bash
cd frontend
npm install
npm run dev

```

---

## Deployment & Production

The system is optimized for split-stack deployment:

1. **Backend (Railway):** Point the service to your GitHub repository. Ensure `LLM_MODEL` is set to `openai/gpt-oss-20b` in the Railway Variables dashboard.
2. **Frontend (Vercel):** Connect the frontend repository. Set `NEXT_PUBLIC_API_URL` to your production Railway backend URL and include the Supabase environment variables.

---

## Security Model

The system operates on a "Isolation-First" principle:

* **Guest Mode:** Utilizes transient session IDs. Data is ephemeral and purged by the backend garbage collector after session expiration.
* **Member Mode:** Utilizes persistent `tenant_id` linked to Google OAuth. Files are strictly partitioned and accessible only to the owner via database-level filtering.

High-Level Summary (The Layman's Note)
If you are wondering how this works: Imagine an AI is a student taking an exam. Usually, a student guesses answers based on what they remember from past lectures (the LLM's training data).

This system works differently. Instead of relying on memory, we give the AI an open-book exam. We provide the AI with a digital copy of your specific documents (the "textbook"). When you ask a question, the system finds the exact page and paragraph relevant to your query and forces the AI to look at that text before writing an answer. Finally, the system adds a citation so you can verify the information yourself.

We’ve also added security "fences" so that if you upload your private notes, other users cannot see them—your documents stay in your own digital workspace.