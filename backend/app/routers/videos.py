from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from ..db import SessionLocal
from .. import models, schemas
from ..storage import upload_file
from ..tasks import pipeline_from_url, pipeline_from_uploaded
from ..ingest import upload_audio_from_url, save_upload_file

router = APIRouter()

class VideoUrlRequest(BaseModel):
    source_url: str
    title: Optional[str] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ingest", response_model=schemas.VideoOut)
async def ingest_video(
    source_url: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    if not source_url and not file:
        raise HTTPException(400, "Provide either source_url or file")

    v = models.Video(source_url=source_url, title=title, status="QUEUED")
    db.add(v); db.commit(); db.refresh(v)

    if source_url:
        pipeline_from_url.delay(v.id, source_url)
    else:
        # save upload to temp and push to S3
        data = await file.read()
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(data)
            tmp.flush()
            s3key = save_upload_file(v.id, tmp.name)
        pipeline_from_uploaded.delay(v.id, s3key)

    return v

@router.post("/ingest_url", response_model=schemas.VideoOut)
def ingest_video_url(request: VideoUrlRequest, db: Session = Depends(get_db)):
    """Ingest a video from URL only (simpler endpoint for URL-only uploads)."""
    v = models.Video(source_url=request.source_url, title=request.title, status="QUEUED")
    db.add(v)
    db.commit()
    db.refresh(v)
    
    # Start the processing pipeline
    pipeline_from_url.delay(v.id, request.source_url)
    
    return v

@router.get("/{video_id}", response_model=schemas.VideoOut)
def get_video(video_id: int, db: Session = Depends(get_db)):
    v = db.get(models.Video, video_id)
    if not v: raise HTTPException(404, "Video not found")
    return v

@router.get("/{video_id}/segments")
def list_segments(video_id: int, db: Session = Depends(get_db)):
    segs = db.query(models.Segment).filter(models.Segment.video_id == video_id).order_by(models.Segment.t_start).all()
    return [
        {"id": s.id, "t_start": s.t_start, "t_end": s.t_end, "text": s.text}
        for s in segs
    ]
