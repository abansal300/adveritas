"""
Verdicts Router

Handles fact-checking verdict generation using LLMs (AWS Bedrock or local models).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from ..db import SessionLocal
from .. import models
from ..verdict_tasks import generate_for_claim

router = APIRouter()

def get_db():
    """Database session dependency for request handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/claim/{claim_id}/generate")
def trigger_verdict(claim_id: int, db: Session = Depends(get_db)):
    """
    Trigger async verdict generation for a claim using collected evidence.
    
    Args:
        claim_id: ID of the claim to generate verdict for
        db: Database session
        
    Returns:
        Status response with queue confirmation
        
    Raises:
        HTTPException: 404 if claim not found
    """
    if not db.get(models.Claim, claim_id):
        raise HTTPException(404, "Claim not found")
    generate_for_claim.delay(claim_id)
    return {"ok": True, "queued": True, "claim_id": claim_id}

@router.get("/claim/{claim_id}")
def get_latest_verdict(claim_id: int, db: Session = Depends(get_db)):
    """
    Get the latest verdict for a claim.
    
    Args:
        claim_id: ID of the claim
        db: Database session
        
    Returns:
        Verdict with label, confidence score, rationale, and sources.
        Returns {"ok": False} if no verdict has been generated yet.
    """
    v = (db.query(models.Verdict)
            .filter(models.Verdict.claim_id == claim_id)
            .order_by(models.Verdict.created_at.desc())
            .first())
    if not v:
        return {"ok": False, "reason": "no_verdict"}
    return {
        "ok": True,
        "label": v.label,
        "confidence": v.confidence,
        "rationale": v.rationale,
        "sources": json.loads(v.sources or "[]"),
    }
