from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from pgvector.sqlalchemy import Vector
from .db import Base

# ---------- Video ----------
class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    source_url = Column(String)
    title = Column(String)
    thumbnail_url = Column(String)  # YouTube thumbnail URL
    duration = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    segments = relationship(
        "Segment",
        back_populates="video",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    claims = relationship(
        "Claim",
        back_populates="video",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

# ---------- Segment ----------
class Segment(Base):
    __tablename__ = "segments"
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), index=True, nullable=False)
    t_start = Column(Float)
    t_end = Column(Float)
    text = Column(Text)

    video = relationship("Video", back_populates="segments")
    claims = relationship(                      # optional, if you keep a FK from Claim -> Segment
        "Claim",
        back_populates="segment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

# ---------- Claim ----------
class Claim(Base):
    __tablename__ = "claims"
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), index=True, nullable=False)
    segment_id = Column(Integer, ForeignKey("segments.id", ondelete="SET NULL"), index=True, nullable=True)
    claim_text = Column(Text, nullable=False)
    canonical_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # MISSING BEFORE: define the 'video' side used by Video.claims
    video = relationship("Video", back_populates="claims")
    # Match Segment.claims above (only if you keep segment_id)
    segment = relationship("Segment", back_populates="claims")

    evidence = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan", passive_deletes=True)
    verdicts = relationship("Verdict", back_populates="claim", cascade="all, delete-orphan", passive_deletes=True)

# ---------- Evidence ----------
class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), index=True, nullable=False)
    source = Column(String)
    title = Column(String)
    url = Column(String)
    snippet = Column(Text)
    similarity = Column(Float)
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="evidence")

# ---------- Verdict ----------
class Verdict(Base):
    __tablename__ = "verdicts"
    id = Column(Integer, primary_key=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), index=True, nullable=False)
    label = Column(String)
    confidence = Column(Float)
    rationale = Column(Text)
    sources = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="verdicts")
