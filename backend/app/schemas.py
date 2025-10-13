from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VerdictLabel(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    NOT_FOUND = "NOT_FOUND"

class VideoCreate(BaseModel):
    source_url: Optional[str] = None
    title: Optional[str] = None

class VideoOut(BaseModel):
    id: int
    source_url: Optional[str] = None
    title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    status: str
    created_at: datetime
    class Config: from_attributes = True

class ClaimOut(BaseModel):
    id: int
    video_id: int
    segment_id: int
    claim_text: str
    canonical_text: Optional[str] = None
    class Config: from_attributes = True

class VerdictOut(BaseModel):
    id: int
    claim_id: int
    label: VerdictLabel
    confidence: Optional[float] = None
    rationale: Optional[str] = None
    class Config: from_attributes = True
