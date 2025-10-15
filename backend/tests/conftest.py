"""
Pytest configuration and fixtures for AdVeritas tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app import models


@pytest.fixture(scope="session")
def db_engine():
    """
    Create test database engine using in-memory SQLite.
    
    Note: This is for basic unit tests. For integration tests with pgvector,
    you'll need a real PostgreSQL database.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """
    Create a test database session for each test.
    
    The session is rolled back after each test to ensure test isolation.
    """
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_video(db_session):
    """Create a sample video for testing."""
    video = models.Video(
        source_url="https://www.youtube.com/watch?v=test123",
        title="Test Video",
        status="TRANSCRIBED",
        duration=120.5
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


@pytest.fixture
def sample_claim(db_session, sample_video):
    """Create a sample claim for testing."""
    claim = models.Claim(
        video_id=sample_video.id,
        claim_text="The Earth is round.",
        canonical_text="The Earth is round."
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)
    return claim


@pytest.fixture
def sample_evidence_rows():
    """Sample evidence data for testing verdict generation."""
    return [
        {
            "title": "Earth - Wikipedia",
            "url": "https://en.wikipedia.org/wiki/Earth",
            "snippet": "Earth is the third planet from the Sun and the only astronomical object known to harbor life."
        },
        {
            "title": "Shape of the Earth",
            "url": "https://en.wikipedia.org/wiki/Spherical_Earth",
            "snippet": "Spherical Earth is an approximation of the figure of the Earth as a sphere."
        }
    ]

