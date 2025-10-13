import os
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(_NAME)
    return _model

def embed_texts(texts: List[str]) -> np.ndarray:
    # normalized so cosine == dot
    m = get_model()
    X = m.encode(texts, normalize_embeddings=True)
    return np.asarray(X, dtype=np.float32)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))  # in [-1, 1]
