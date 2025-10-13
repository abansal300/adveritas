import json
from .celery_app import celery_app
from .db import SessionLocal
from . import models
from .verdicts import generate_verdict

@celery_app.task(name="verdicts.generate_for_claim")
def generate_for_claim(claim_id: int):
    db = SessionLocal()
    try:
        claim = db.get(models.Claim, claim_id)
        if not claim:
            return {"ok": False, "reason": "no_claim"}
        # fetch top evidence already sorted by similarity desc (nulls last)
        evs = (db.query(models.Evidence)
                 .filter(models.Evidence.claim_id == claim_id)
                 .order_by(models.Evidence.similarity.desc().nullslast())
                 .limit(10).all())
        rows = [{"title": e.title or "", "url": e.url or "", "snippet": e.snippet or ""} for e in evs]
        out = generate_verdict(claim.canonical_text or claim.claim_text, rows)
        v = models.Verdict(
            claim_id=claim_id,
            label=out["label"],
            confidence=out["confidence"],
            rationale=out["rationale"],
            sources=json.dumps(out["sources"]),
        )
        db.add(v); db.commit()
        return {"ok": True, "label": v.label, "confidence": v.confidence}
    finally:
        db.close()
