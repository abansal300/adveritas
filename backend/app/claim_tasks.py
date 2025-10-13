from .celery_app import celery_app
from .db import SessionLocal
from . import models
from .claims_extract import extract_claim_sentences
from sqlalchemy.orm import Session


@celery_app.task(name="claims.extract_for_video")
def extract_for_video(video_id: int, overwrite: bool = False):
    db: Session = SessionLocal()
    try:
        # 1) gather all segments in order
        segs = (
            db.query(models.Segment)
              .filter(models.Segment.video_id == video_id)
              .order_by(models.Segment.t_start.asc())
              .all()
        )
        if not segs:
            return {"ok": False, "reason": "no_segments"}

        # optionally wipe old claims (useful in dev)
        if overwrite:
            db.query(models.Claim).filter(models.Claim.video_id == video_id).delete()
            db.commit()

        # 2) extract per segment to retain timestamps
        created = 0
        for seg in segs:
            cand = extract_claim_sentences(seg.text)
            for text, score in cand:
                db.add(models.Claim(
                    video_id=video_id,
                    segment_id=seg.id,
                    claim_text=text,
                    canonical_text=text,  # later you'll normalize entities, dates, etc.
                ))
                created += 1

        # 3) mark video status
        v = db.get(models.Video, video_id)
        if v:
            v.status = "CLAIMED" if created else "NO_CLAIMS"
        db.commit()
        return {"ok": True, "created": created}
    finally:
        db.close()
