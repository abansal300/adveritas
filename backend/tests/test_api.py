"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import models


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns success."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "Adveritas" in response.json()["message"]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["service"] == "api"


class TestVideoEndpoints:
    """Tests for video-related endpoints."""
    
    def test_get_nonexistent_video(self, client):
        """Test getting a video that doesn't exist returns 404."""
        response = client.get("/videos/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestClaimEndpoints:
    """Tests for claim-related endpoints."""
    
    def test_extract_claims_nonexistent_video(self, client):
        """Test extracting claims for nonexistent video returns 404."""
        response = client.post("/claims/video/99999/extract")
        assert response.status_code == 404


class TestEvidenceEndpoints:
    """Tests for evidence-related endpoints."""
    
    def test_fetch_evidence_nonexistent_claim(self, client):
        """Test fetching evidence for nonexistent claim returns 404."""
        response = client.post("/evidence/claim/99999/fetch")
        assert response.status_code == 404


class TestVerdictEndpoints:
    """Tests for verdict-related endpoints."""
    
    def test_generate_verdict_nonexistent_claim(self, client):
        """Test generating verdict for nonexistent claim returns 404."""
        response = client.post("/verdicts/claim/99999/generate")
        assert response.status_code == 404
    
    def test_get_verdict_nonexistent_claim(self, client):
        """Test getting verdict for nonexistent claim returns no verdict."""
        response = client.get("/verdicts/claim/99999")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False
        assert data["reason"] == "no_verdict"

