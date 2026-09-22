# RepoMind — Gemini AI Codebase Intelligence Platform

## What it does
RepoMind ingests a public GitHub repository and answers questions about its code using a RAG pipeline.

## Pipeline
GitHub → parsing → chunking → Sentence Transformers → pgvector + BM25 → Reciprocal Rank Fusion → Cross-Encoder reranking → Gemini → cited answer

## Requirements
- Python 3.11+
- Node.js 20+
- Docker Desktop (recommended)
- Gemini API key

## Quick start

### 1. Start PostgreSQL + pgvector
From the project root:
```bash
docker compose up -d db
```

### 2. Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

Put your Gemini API key in `backend/.env`, then:
```bash
uvicorn app.main:app --reload
```

API: http://localhost:8000
Swagger: http://localhost:8000/docs

### 3. Frontend
Open another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

### 4. Use
1. Paste a public GitHub repository URL.
2. Click Index Repository.
3. Select the repository.
4. Ask codebase questions.

## Gemini
Gemini is the only generation model. Embeddings and reranking run locally with Sentence Transformers.

Google's model names and quotas can change, so verify the current Google AI Studio documentation when creating your API key.

## Production improvements
Add authentication, background indexing jobs, rate limiting, repository size limits, AST-aware chunking, caching, evaluation datasets, and streaming Gemini responses.
