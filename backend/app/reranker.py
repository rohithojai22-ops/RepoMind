from sentence_transformers import CrossEncoder

_model = None

def get_reranker():
    global _model
    if _model is None:
        _model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _model

def rerank(query, chunks, top_k=8):
    if not chunks:
        return []
    scores = get_reranker().predict([(query,c.content) for c in chunks])
    ranked = sorted(zip(chunks,scores), key=lambda x:float(x[1]), reverse=True)
    return [c for c,_ in ranked[:top_k]]
