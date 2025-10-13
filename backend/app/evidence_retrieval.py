# app/evidence_retrieval.py
import os
from typing import List, Dict
import wikipedia
import requests

from .embeddings import embed_texts, cosine_sim
from .db import SessionLocal
from . import models

NEWS_KEY = os.getenv("NEWSAPI_KEY")

def get_wiki_evidence(query: str, topk: int = 3) -> List[Dict]:
    out: List[Dict] = []
    for title in wikipedia.search(query, results=topk):
        try:
            page = wikipedia.page(title, auto_suggest=False)
            out.append({
                "source": "wikipedia",
                "title": title,
                "url": page.url,
                "snippet": (page.summary or "")[:600],
            })
        except Exception:
            pass
    return out

def get_news_evidence(query: str, topk: int = 3) -> List[Dict]:
    if not NEWS_KEY:
        return []
    try:
        r = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "apiKey": NEWS_KEY, "pageSize": topk, "language": "en"},
            timeout=15,
        )
        r.raise_for_status()
        arts = r.json().get("articles", [])
        return [{
            "source": "newsapi",
            "title": a.get("title") or "",
            "url": a.get("url") or "",
            "snippet": (a.get("description") or "")[:600],
        } for a in arts]
    except Exception:
        return []

def store_evidence(claim_id: int, items: List[Dict]) -> int:
    """Embeds claim + items, stores rows with cosine similarity; returns count."""
    if not items:
        return 0

    db = SessionLocal()
    try:
        claim = db.get(models.Claim, claim_id)
        if not claim:
            return 0

        qtext = (claim.canonical_text or claim.claim_text or "").strip()
        q_vec = embed_texts([qtext])[0]  # normalized

        snippets = [(i.get("snippet") or "").strip() for i in items]
        e_mat = embed_texts(snippets) if snippets else []

        created = 0
        for i, itm in enumerate(items):
            sim = cosine_sim(q_vec, e_mat[i]) if len(e_mat) > i else None
            db.add(models.Evidence(
                claim_id=claim_id,
                source=itm.get("source"),
                title=itm.get("title"),
                url=itm.get("url"),
                snippet=snippets[i],
                similarity=sim,
                embedding=e_mat[i].tolist() if len(e_mat) > i else None,
            ))
            created += 1
        db.commit()
        return created
    finally:
        db.close()
