from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..evidence_tasks import fetch_for_claim

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/claim/{claim_id}/fetch")
def trigger_evidence(claim_id: int, db: Session = Depends(get_db)):
    c = db.get(models.Claim, claim_id)
    if not c: raise HTTPException(404, "Claim not found")
    fetch_for_claim.delay(claim_id)
    return {"ok": True, "queued": True}

@router.get("/claim/{claim_id}")
def list_evidence(claim_id: int, db: Session = Depends(get_db)):
    rows = (db.query(models.Evidence)
              .filter(models.Evidence.claim_id == claim_id)
              .order_by(models.Evidence.similarity.desc().nullslast())
              .all())
    return [
        {
            "id": r.id,
            "title": r.title,
            "source": r.source,
            "url": r.url,
            "snippet": r.snippet,
            "similarity": r.similarity,
        }
        for r in rows
    ]
