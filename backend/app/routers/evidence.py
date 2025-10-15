"""
Evidence Router

Handles evidence retrieval from web sources and Wikipedia for fact-checking claims.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..evidence_tasks import fetch_for_claim

router = APIRouter()

def get_db():
    """Database session dependency for request handlers."""
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/claim/{claim_id}/fetch")
def trigger_evidence(claim_id: int, db: Session = Depends(get_db)):
    """
    Trigger async evidence retrieval for a claim.
    
    Args:
        claim_id: ID of the claim to find evidence for
        db: Database session
        
    Returns:
        Status response with queue confirmation
        
    Raises:
        HTTPException: 404 if claim not found
    """
    c = db.get(models.Claim, claim_id)
    if not c: raise HTTPException(404, "Claim not found")
    fetch_for_claim.delay(claim_id)
    return {"ok": True, "queued": True}

@router.get("/claim/{claim_id}")
def list_evidence(claim_id: int, db: Session = Depends(get_db)):
    """
    List all evidence items for a claim, ordered by similarity score.
    
    Args:
        claim_id: ID of the claim
        db: Database session
        
    Returns:
        List of evidence items with sources, snippets, and similarity scores
    """
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
