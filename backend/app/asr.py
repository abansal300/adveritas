import os, tempfile
from typing import List, Tuple
from faster_whisper import WhisperModel
from .storage import download_file
from .db import SessionLocal
from . import models

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # base/small/medium/large-v3
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu") # "cuda" if you have GPU

_model = None
def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type="int8")
    return _model

def transcribe_s3_to_segments(s3_key: str) -> List[Tuple[float,float,str]]:
    """Downloads audio from S3, runs ASR, returns [(start,end,text), ...]."""
    with tempfile.TemporaryDirectory() as td:
        local = os.path.join(td, "audio.mp3")
        download_file(s3_key, local)
        model = get_model()
        
        # Try with VAD filter first, fallback without if it removes all content
        try:
            segments, info = model.transcribe(local, vad_filter=True, word_timestamps=False)
            segment_list = list(segments)
            
            # If VAD removed everything, try without VAD
            if not segment_list:
                print("VAD filter removed all content, retrying without VAD...")
                segments, info = model.transcribe(local, vad_filter=False, word_timestamps=False)
                segment_list = list(segments)
                
        except ValueError as e:
            if "max() arg is an empty sequence" in str(e):
                print("Language detection failed, retrying without VAD...")
                segments, info = model.transcribe(local, vad_filter=False, word_timestamps=False)
                segment_list = list(segments)
            else:
                raise
        
        out = []
        for seg in segment_list:
            if seg.text.strip():  # Only add non-empty segments
                out.append((float(seg.start), float(seg.end), seg.text.strip()))
        
        if not out:
            print("Warning: No speech segments found in audio")
            # Add a placeholder segment to avoid empty results
            out.append((0.0, 1.0, "[No speech detected]"))
            
        return out

def persist_segments(video_id: int, segments: List[Tuple[float,float,str]]):
    db = SessionLocal()
    try:
        for (s,e,t) in segments:
            db.add(models.Segment(video_id=video_id, t_start=s, t_end=e, text=t))
        
        v = db.get(models.Video, video_id)
        if v:
            # Set status based on whether we found actual speech
            if any("[No speech detected]" not in t for s,e,t in segments):
                v.status = "TRANSCRIBED"
            else:
                v.status = "NO_SPEECH"
        db.commit()
    except Exception as e:
        print(f"Error persisting segments for video {video_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()
