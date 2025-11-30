from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .embeddings import embed_texts

def retrieve_top_k(
    chunks: List[Tuple[str, str]],
    question: str,
    k: int = 5,
) -> List[Tuple[str, str]]:
    """
    chunks: list of (source_label, chunk_text)
    returns top-k (source_label, chunk_text)
    """
    if not chunks:
        return []

    texts = [c[1] for c in chunks]
    chunk_emb = embed_texts(texts)
    q_emb = embed_texts([question])[0].reshape(1, -1)

    sims = cosine_similarity(q_emb, chunk_emb)[0]
    top_idx = np.argsort(sims)[::-1][:k]

    return [chunks[i] for i in top_idx]
