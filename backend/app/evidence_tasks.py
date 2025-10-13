# app/evidence_tasks.py
from .celery_app import celery_app
from .db import SessionLocal
from . import models

@celery_app.task(name="evidence.fetch_for_claim")
def fetch_for_claim(claim_id: int):
    # Lazy import avoids circular import during app startup
    from .evidence_retrieval import get_wiki_evidence, get_news_evidence, store_evidence

    db = SessionLocal()
    try:
        claim = db.get(models.Claim, claim_id)
        if not claim:
            return {"ok": False, "reason": "no_claim"}

        query = claim.canonical_text or claim.claim_text
        items = get_wiki_evidence(query, topk=3) + get_news_evidence(query, topk=2)
        count = store_evidence(claim_id, items)
        return {"ok": True, "stored": count}
    finally:
        db.close()
