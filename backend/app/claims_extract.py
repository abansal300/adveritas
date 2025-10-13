import os
from typing import List, Tuple, Optional
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize

# Ensure punkt tokenizer once per image
nltk.download("punkt", quiet=True)

_CLAIM_MODEL = os.getenv("CLAIM_ZS_MODEL", "facebook/bart-large-mnli")
_MIN_SCORE   = float(os.getenv("CLAIM_MIN_SCORE", "0.55"))

# Lazy global
_zs = None
def get_zs():
    global _zs
    if _zs is None:
        _zs = pipeline("zero-shot-classification", model=_CLAIM_MODEL)
    return _zs

# Labels we’ll classify each sentence into
LABELS = ["verifiable factual claim", "opinion / rhetoric", "question", "instruction"]

def sentence_split(text: str) -> List[str]:
    # Basic cleanup then NLTK sentence split
    text = (text or "").replace("\n", " ").strip()
    if not text:
        return []
    return [s.strip() for s in sent_tokenize(text) if s.strip()]

def score_claim(sentence: str) -> float:
    """Return the probability that a sentence is a verifiable factual claim."""
    clf = get_zs()
    out = clf(sentence, LABELS, multi_label=False)
    # Normalize name match; first label is our positive class
    # HF may reorder labels by score in `out["labels"]`
    scores = dict(zip(out["labels"], out["scores"]))
    return float(scores.get("verifiable factual claim", 0.0))

def extract_claim_sentences(text: str, min_score: float = _MIN_SCORE) -> List[Tuple[str,float]]:
    claims = []
    for s in sentence_split(text):
        p = score_claim(s)
        if p >= min_score:
            claims.append((s, p))
    return claims
