# AdVeritas 🔍

**AI-Powered Automated Fact-Checking for Video Content**

AdVeritas is a full-stack application that automatically transcribes YouTube videos, extracts factual claims, retrieves evidence from the web, and generates fact-checking verdicts using AI models.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

- **🎥 YouTube Video Processing**: Automatically download and transcribe video audio using Faster-Whisper
- **💬 Claim Extraction**: AI-powered extraction of factual claims from transcripts using NLP techniques
- **🔎 Evidence Retrieval**: Semantic search across Wikipedia and web sources with vector embeddings
- **⚖️ Verdict Generation**: LLM-based fact-checking with confidence scores and rationales
- **🎨 Modern UI**: Beautiful Next.js frontend with real-time updates and responsive design
- **⚡ Async Processing**: Celery-based distributed task queue for background processing
- **🔄 Scalable Architecture**: Microservices-ready design with Docker support

## 🏗️ Architecture

### Backend Stack (FastAPI + Python)
- **FastAPI**: High-performance RESTful API with automatic OpenAPI documentation
- **PostgreSQL + pgvector**: Vector database for semantic similarity search
- **Redis + Celery**: Distributed task queue for async background processing
- **AWS Bedrock / Local Models**: Flexible LLM inference (Llama 3.2)
- **Faster-Whisper**: High-performance speech-to-text transcription
- **Sentence-Transformers**: Semantic embeddings for evidence matching
- **SQLAlchemy + Alembic**: ORM and database migrations

### Frontend Stack (Next.js + TypeScript)
- **Next.js 15**: React framework with App Router and SSR
- **TypeScript**: Type-safe development experience
- **Tailwind CSS**: Utility-first CSS for modern, responsive UI
- **Real-time Polling**: Live status updates during video processing

## 📁 Project Structure

```
adveritas/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── routers/           # API route handlers
│   │   │   ├── videos.py      # Video ingestion endpoints
│   │   │   ├── claims.py      # Claim extraction endpoints
│   │   │   ├── evidence.py    # Evidence retrieval endpoints
│   │   │   └── verdicts.py    # Verdict generation endpoints
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── schemas.py         # Pydantic schemas for validation
│   │   ├── verdicts.py        # LLM verdict generation logic
│   │   ├── asr.py             # Speech recognition with Whisper
│   │   ├── embeddings.py      # Vector embedding generation
│   │   ├── evidence_retrieval.py  # Web search and Wikipedia
│   │   ├── celery_app.py      # Celery configuration
│   │   ├── *_tasks.py         # Async task definitions
│   │   └── db.py              # Database configuration
│   ├── Dockerfile             # Backend container image
│   └── pyproject.toml         # Python dependencies
├── frontend/                   # Next.js application
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx       # Main UI component
│   │       ├── layout.tsx     # App layout wrapper
│   │       └── globals.css    # Global styles
│   ├── Dockerfile             # Frontend container image
│   └── package.json           # Node dependencies
├── docker-compose.yml          # Local development orchestration
├── README.md                   # This file
├── DEVELOPMENT.md              # Setup and contribution guide
└── DEPLOYMENT_CHECKLIST.md     # Production deployment guide
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

The fastest way to get started is using Docker Compose, which sets up all services automatically.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/adveritas.git
cd adveritas

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

For development or if you prefer manual setup, see [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed instructions.

## 📊 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive Swagger/OpenAPI documentation.

### Key Endpoints

**Videos**
- `POST /videos/ingest` - Upload a YouTube URL for processing
- `GET /videos/{id}` - Get video status and metadata

**Claims**
- `POST /claims/video/{id}/extract` - Extract claims from video transcript
- `GET /claims/video/{id}` - List all claims for a video

**Evidence**
- `POST /evidence/claim/{id}/fetch` - Retrieve evidence for a claim
- `GET /evidence/claim/{id}` - List all evidence for a claim

**Verdicts**
- `POST /verdicts/claim/{id}/generate` - Generate fact-checking verdict
- `GET /verdicts/claim/{id}` - Get verdict for a claim

## 🔧 Configuration

### Backend Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/adveritas

# Redis & Celery
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
USE_BEDROCK=false                                    # Use AWS Bedrock (true) or local (false)
BEDROCK_MODEL_ID=meta.llama3-2-3b-instruct-v1:0     # AWS Bedrock model
VERDICT_MODEL=gpt2-medium                            # Local model fallback
AWS_REGION=us-east-1

# Embeddings
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Storage (optional)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=adveritas

# Model Parameters
CLAIM_MIN_SCORE=0.35                                 # Minimum claim confidence threshold
VERDICT_TOPK=5                                       # Number of evidence items to use
```

### Frontend Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install pytest pytest-cov
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```
---

