from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from . import models

# Routers
from .routers import videos, claims, evidence, verdicts

# Celery app import (so workers register tasks)
from .celery_app import celery_app


# -----------------------------------------------------------
# Initialize FastAPI
# -----------------------------------------------------------
app = FastAPI(
    title="Adveritas API",
    version="1.0",
    description="Backend for automated claim verification from YouTube videos."
)

# -----------------------------------------------------------
# CORS Middleware (so frontend can call backend)
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# Database setup
# -----------------------------------------------------------
# Enable pgvector extension before creating tables
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)


# -----------------------------------------------------------
# Register routers
# -----------------------------------------------------------
app.include_router(videos.router, prefix="/videos", tags=["videos"])
app.include_router(claims.router, prefix="/claims", tags=["claims"])
app.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
app.include_router(verdicts.router, prefix="/verdicts", tags=["verdicts"])


# -----------------------------------------------------------
# Root + Health endpoint
# -----------------------------------------------------------
@app.get("/")
def read_root():
    return {"message": "Adveritas API is running."}


@app.get("/health")
def health_check():
    return {"ok": True, "service": "api"}


# -----------------------------------------------------------
# Celery task trigger example (optional)
# -----------------------------------------------------------
@app.post("/tasks/test")
def test_task():
    from .tasks import example_task
    example_task.delay()
    return {"queued": True}
