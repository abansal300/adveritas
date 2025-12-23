# AdVeritas

> **AI-Powered Fact-Checking Platform for Video Content**

AdVeritas automatically transcribes YouTube videos, extracts verifiable claims using NLP, retrieves supporting evidence through semantic search, and generates AI-powered fact-checking verdicts with confidence scores.

## 🎯 Overview

AdVeritas tackles the challenge of misinformation in online video content by automating the fact-checking process. The platform:

1. **Transcribes** YouTube videos using state-of-the-art speech recognition
2. **Extracts** factual claims using natural language processing and LLMs
3. **Retrieves** relevant evidence from Wikipedia and web sources using semantic search
4. **Generates** fact-checking verdicts with confidence scores and detailed rationales

**Perfect for:** Researchers, journalists, educators, and anyone who wants to verify information in video content.

---

## 🌟 Key Features

### Core Functionality
- ✅ **Automated Video Processing** - Download and transcribe YouTube videos with Faster-Whisper
- ✅ **AI Claim Extraction** - Identify verifiable statements using NLP and transformer models
- ✅ **Semantic Evidence Search** - Find relevant sources using vector embeddings and pgvector
- ✅ **LLM-Powered Verdicts** - Generate fact-checking assessments with AWS Bedrock (Llama 3.2)
- ✅ **Real-Time Updates** - Live status tracking during async background processing
- ✅ **Interactive API** - Full RESTful API with automatic OpenAPI/Swagger documentation

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js UI    │  ← User Interface
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│   FastAPI       │  ← RESTful API Server
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│ Redis │ │PostgreSQL│  ← Data Stores
│ Queue │ │+pgvector │
└───┬───┘ └─────────┘
    │
┌───▼────────┐
│   Celery   │  ← Background Workers
│  Workers   │  (Transcription, ML Tasks)
└────────────┘
```

### Data Flow
1. User submits YouTube URL via frontend
2. API validates and queues video for processing
3. Celery worker downloads and transcribes video
4. Claims are extracted using NLP and stored in PostgreSQL
5. Evidence is retrieved using semantic search (vector embeddings)
6. LLM generates fact-checking verdict
7. Results are displayed in real-time to user

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async web framework |
| **PostgreSQL + pgvector** | Relational database with vector similarity search |
| **Redis** | In-memory cache and message broker |
| **Celery** | Distributed task queue for background processing |
| **SQLAlchemy** | Python SQL toolkit and ORM |
| **Alembic** | Database migration tool |
| **Pydantic** | Data validation using Python type hints |

### Machine Learning & AI
| Technology | Purpose |
|------------|---------|
| **AWS Bedrock** | Managed LLM inference (Llama 3.2) |
| **Faster-Whisper** | Speech-to-text transcription |
| **Sentence-Transformers** | Text embeddings for semantic search |
| **NLTK** | Natural language processing toolkit |
| **Transformers (Hugging Face)** | State-of-the-art NLP models |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 15** | React framework with App Router |
| **TypeScript** | Type-safe JavaScript |
| **Tailwind CSS** | Utility-first CSS framework |
| **React** | UI component library |

### DevOps & Tools
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **pytest** | Python testing framework |
| **ESLint** | JavaScript/TypeScript linting |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/abansal300/adveritas.git
cd adveritas

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed local development setup instructions.

---

## 📁 Project Structure

```
adveritas/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── routers/           # API route handlers
│   │   │   ├── videos.py      # Video ingestion endpoints
│   │   │   ├── claims.py      # Claim extraction endpoints
│   │   │   ├── evidence.py    # Evidence retrieval endpoints
│   │   │   └── verdicts.py    # Verdict generation endpoints
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── verdicts.py        # LLM verdict generation logic
│   │   ├── asr.py             # Speech recognition (Whisper)
│   │   ├── embeddings.py      # Vector embedding generation
│   │   ├── evidence_retrieval.py  # Evidence search logic
│   │   ├── celery_app.py      # Celery configuration
│   │   ├── *_tasks.py         # Async task definitions
│   │   └── db.py              # Database connection setup
│   ├── tests/                 # Backend test suite
│   ├── Dockerfile             # Backend container image
│   ├── pyproject.toml         # Python dependencies (pip)
│   └── requirements.txt       # Alternative dependency list
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx       # Main UI component
│   │       ├── layout.tsx     # App layout wrapper
│   │       └── globals.css    # Global styles
│   ├── Dockerfile             # Frontend container image
│   ├── package.json           # Node.js dependencies
│   └── tsconfig.json          # TypeScript configuration
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md          # Deployment guides
│   └── API.md                 # API reference
├── docker-compose.yml          # Local development orchestration
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```

---

## 📊 API Documentation

The API provides comprehensive RESTful endpoints for all fact-checking operations.

### Core Endpoints

#### Videos
```
POST   /videos/ingest              Upload YouTube URL for processing
GET    /videos/{id}                Get video details and status
```

#### Claims
```
POST   /claims/video/{id}/extract  Extract claims from transcript
GET    /claims/video/{id}          List all claims for video
GET    /claims/{id}                Get specific claim details
```

#### Evidence
```
POST   /evidence/claim/{id}/fetch  Retrieve evidence for claim
GET    /evidence/claim/{id}        List all evidence for claim
```

#### Verdicts
```
POST   /verdicts/claim/{id}/generate  Generate fact-checking verdict
GET    /verdicts/claim/{id}           Get verdict details
```

### Interactive Documentation

When running locally, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🌐 Deployment

AdVeritas is designed for cloud deployment with frontend and backend on separate platforms.

### Production Deployment

- **Frontend**: Deploy to Vercel (Next.js optimized)
- **Backend**: Deploy to Railway, Render, or AWS
- **Database**: Managed PostgreSQL (Railway/RDS)
- **Cache**: Managed Redis (Railway/ElastiCache)

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python formatting
black backend/

# Python linting
ruff check backend/

# TypeScript linting
cd frontend && npm run lint
```
---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Next.js](https://nextjs.org/) for the React framework
- [Hugging Face](https://huggingface.co/) for transformer models
- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- AWS Bedrock for LLM infrastructure

---
