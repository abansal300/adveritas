import os
from celery import Celery
from .ingest import upload_audio_from_url, save_upload_file, get_video_metadata
from .asr import transcribe_s3_to_segments, persist_segments
from .db import SessionLocal
from . import models
from .celery_app import celery_app

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name="pipeline.from_url")
def pipeline_from_url(video_id: int, url: str):
    # Extract and save video metadata
    db = SessionLocal()
    try:
        metadata = get_video_metadata(url)
        video = db.get(models.Video, video_id)
        if video:
            if metadata.get("title") and not video.title:
                video.title = metadata["title"]
            if metadata.get("thumbnail_url"):
                video.thumbnail_url = metadata["thumbnail_url"]
            if metadata.get("duration"):
                video.duration = metadata["duration"]
            db.commit()
    finally:
        db.close()
    
    key = upload_audio_from_url(video_id, url)
    segs = transcribe_s3_to_segments(key)
    persist_segments(video_id, segs)

@celery_app.task(name="pipeline.from_uploaded")
def pipeline_from_uploaded(video_id: int, s3_key: str):
    segs = transcribe_s3_to_segments(s3_key)
    persist_segments(video_id, segs)