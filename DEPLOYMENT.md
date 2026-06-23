# Deployment Guide

This repository is a monorepo:

- `backend/` is the FastAPI service for Railway.
- `frontend/` is the Next.js app for Vercel.

## Railway Backend

Recommended Railway service settings:

- Root Directory: `backend`
- Config File Path: `/backend/railway.toml`
- Public networking: enabled
- Healthcheck path: `/health`

Required Railway variables:

```env
GROQ_API_KEY=your_groq_api_key_here
FRONTEND_ORIGIN=https://rag-intelligence-system.vercel.app
```

If Railway is still pointed at the repository root, the root `Dockerfile` and
root `railway.toml` will still build the backend. Setting the root directory to
`backend` is cleaner and avoids uploading the frontend during backend builds.

After deploy, verify:

```text
https://your-railway-domain.up.railway.app/health
```

It should return:

```json
{"status":"healthy","version":"1.0.0"}
```

## Vercel Frontend

Recommended Vercel project settings:

- Root Directory: `frontend`
- Framework Preset: Next.js
- Install Command: `npm ci`
- Build Command: `npm run build`

Required Vercel variable:

```env
NEXT_PUBLIC_API_URL=https://your-railway-domain.up.railway.app
```

Redeploy the Vercel app after changing `NEXT_PUBLIC_API_URL`; public Next.js
environment variables are baked into the client bundle during the build.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm ci
copy .env.example .env.local
npm run dev
```
