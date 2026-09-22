from collections import defaultdict
from rank_bm25 import BM25Okapi
from sqlalchemy import select
from .database import SessionLocal
from .models import CodeChunk
from .embeddings import embed_query

def hybrid_search(repo_id, query, top_k=8):
    db = SessionLocal()
    try:
        chunks = db.scalars(select(CodeChunk).where(CodeChunk.repository_id == repo_id)).all()
        if not chunks:
            return []

        qvec = embed_query(query)
        vector_rows = db.scalars(
            select(CodeChunk)
            .where(CodeChunk.repository_id == repo_id)
            .order_by(CodeChunk.embedding.cosine_distance(qvec))
            .limit(top_k * 3)
        ).all()

        vector_rank = {c.id:i for i,c in enumerate(vector_rows)}
        tokenized = [c.content.lower().split() for c in chunks]
        bm25 = BM25Okapi(tokenized)
        scores = bm25.get_scores(query.lower().split())
        order = sorted(range(len(chunks)), key=lambda i:scores[i], reverse=True)[:top_k*3]
        bm_rank = {chunks[i].id:r for r,i in enumerate(order)}

        fused = defaultdict(float)
        for cid,r in vector_rank.items():
            fused[cid] += 1/(60+r+1)
        for cid,r in bm_rank.items():
            fused[cid] += 1/(60+r+1)

        by_id = {c.id:c for c in chunks}
        ranked = sorted(fused.items(), key=lambda x:x[1], reverse=True)[:top_k*2]
        return [by_id[cid] for cid,_ in ranked]
    finally:
        db.close()
