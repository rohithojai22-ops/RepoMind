from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select, delete
from .database import SessionLocal
from .models import Repository, CodeChunk
from .github import fetch_repo_files
from .chunker import chunk_code
from .embeddings import embed_texts
from .retrieval import hybrid_search
from .reranker import rerank
from .gemini import answer_with_gemini

router = APIRouter()

class IngestRequest(BaseModel):
    url: HttpUrl

class ChatRequest(BaseModel):
    repository_id: int
    question: str

@router.post("/repositories")
async def ingest_repository(req: IngestRequest):
    url = str(req.url)
    try:
        owner,name,files = await fetch_repo_files(url)
    except Exception as e:
        raise HTTPException(400, f"GitHub ingestion failed: {e}")

    db = SessionLocal()
    try:
        repo = db.scalar(select(Repository).where(Repository.url == url))
        if repo:
            db.execute(delete(CodeChunk).where(CodeChunk.repository_id == repo.id))
            repo.name,repo.owner,repo.status = name,owner,"indexing"
        else:
            repo = Repository(url=url,name=name,owner=owner,status="indexing")
            db.add(repo)
            db.flush()

        chunks = []
        for f in files:
            chunks.extend(chunk_code(f["path"],f["language"],f["content"]))

        if not chunks:
            raise HTTPException(400,"No supported text/code files found.")

        vectors = embed_texts([c["content"] for c in chunks])
        for c,vec in zip(chunks,vectors):
            db.add(CodeChunk(
                repository_id=repo.id,path=c["path"],language=c["language"],
                start_line=c["start_line"],end_line=c["end_line"],
                content=c["content"],embedding=vec
            ))
        repo.status="ready"
        db.commit()
        return {"repository_id":repo.id,"name":repo.name,"owner":repo.owner,
                "files":len(files),"chunks":len(chunks),"status":repo.status}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500,str(e))
    finally:
        db.close()

@router.get("/repositories")
def list_repositories():
    db = SessionLocal()
    try:
        repos = db.scalars(select(Repository).order_by(Repository.created_at.desc())).all()
        return [{"id":r.id,"name":r.name,"owner":r.owner,"url":r.url,"status":r.status} for r in repos]
    finally:
        db.close()

@router.post("/chat")
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400,"Question cannot be empty.")
    db = SessionLocal()
    try:
        if not db.get(Repository,req.repository_id):
            raise HTTPException(404,"Repository not found.")
    finally:
        db.close()

    candidates = hybrid_search(req.repository_id,req.question)
    selected = rerank(req.question,candidates)
    answer = answer_with_gemini(req.question,selected)

    return {
        "answer":answer,
        "sources":[
            {"path":c.path,"start_line":c.start_line,"end_line":c.end_line,"language":c.language}
            for c in selected
        ]
    }
