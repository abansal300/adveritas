from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models, schemas
from ..claim_tasks import extract_for_video

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/video/{video_id}/extract")
def trigger_extract(video_id: int, overwrite: bool = False, db: Session = Depends(get_db)):
    v = db.get(models.Video, video_id)
    if not v:
        raise HTTPException(404, "Video not found")
    # enqueue
    extract_for_video.delay(video_id, overwrite)
    return {"ok": True, "queued": True, "video_id": video_id}
    
@router.get("/video/{video_id}", response_model=list[schemas.ClaimOut])
def list_claims(video_id: int, db: Session = Depends(get_db)):
    claims = db.query(models.Claim).filter(models.Claim.video_id == video_id).all()
    return claims
