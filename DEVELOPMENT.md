# Development Guide

This guide will help you set up AdVeritas for local development and contribution.

## 📋 Prerequisites

- **Python 3.11+** (Python 3.12 recommended)
- **Node.js 18+** and npm
- **PostgreSQL 15+** with pgvector extension
- **Redis 6+**
- **Git** for version control
- **Docker & Docker Compose** (optional, for containerized development)

## 🚀 Quick Start with Docker Compose

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/adveritas.git
cd adveritas

# Start all services (PostgreSQL, Redis, API, Worker, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🛠️ Manual Development Setup

If you prefer to run services manually or need more control:

### 1. Backend Setup

#### Install PostgreSQL with pgvector

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
psql postgres -c "CREATE DATABASE adveritas;"
psql adveritas -c "CREATE EXTENSION vector;"
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE adveritas;"
sudo -u postgres psql adveritas -c "CREATE EXTENSION vector;"
```

#### Install Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

#### Set up Python Environment

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black ruff mypy
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Database
DATABASE_URL=postgresql://localhost/adveritas

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
USE_BEDROCK=false
VERDICT_MODEL=gpt2-medium
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# For AWS Bedrock (optional)
# USE_BEDROCK=true
# BEDROCK_MODEL_ID=meta.llama3-2-3b-instruct-v1:0
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret

# Storage (optional - for development, files are stored in /tmp)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=adveritas

# Model Parameters
CLAIM_MIN_SCORE=0.35
VERDICT_TOPK=5
```

#### Run Database Migrations

```bash
cd backend
source venv/bin/activate

# Run migrations
alembic upgrade head

# Verify tables were created
psql adveritas -c "\dt"
```

#### Start the Backend API

```bash
cd backend
source venv/bin/activate

# Start FastAPI server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 and docs at http://localhost:8000/docs

#### Start Celery Worker

In a **new terminal**:

```bash
cd backend
source venv/bin/activate

# Start Celery worker
celery -A app.celery_app.celery_app worker --loglevel=INFO

# For development with auto-reload (requires watchdog)
# pip install watchdog
# celery -A app.celery_app.celery_app worker --loglevel=INFO --pool=solo
```

### 2. Frontend Setup

In a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_verdicts.py -v

# Run tests matching pattern
pytest -k "test_parse_json"
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

## 🎨 Code Style & Linting

### Python (Backend)

We use **Black** for formatting, **Ruff** for linting, and **MyPy** for type checking.

```bash
cd backend
source venv/bin/activate

# Format code with Black
black .

# Check formatting
black . --check

# Lint with Ruff
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Type check with MyPy
mypy app/
```

### TypeScript (Frontend)

```bash
cd frontend

# Run ESLint
npm run lint

# Fix ESLint issues
npm run lint -- --fix

# Format with Prettier (if configured)
npm run format
```

### Pre-commit Hooks (Optional)

Install pre-commit hooks to automatically check code before commits:

```bash
cd backend
pip install pre-commit
pre-commit install
```

Now, Black and Ruff will run automatically on every commit.

## 📦 Database Management

### Create a New Migration

After modifying models in `backend/app/models.py`:

```bash
cd backend
source venv/bin/activate

# Auto-generate migration
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration in backend/app/alembic/versions/
# Edit if needed, then apply:
alembic upgrade head
```

### Rollback a Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Reset Database

```bash
# Drop and recreate database
psql postgres -c "DROP DATABASE adveritas;"
psql postgres -c "CREATE DATABASE adveritas;"
psql adveritas -c "CREATE EXTENSION vector;"

# Run migrations
cd backend
alembic upgrade head
```

## 🐛 Debugging

### Backend Debugging

Add breakpoints using Python's `pdb`:

```python
import pdb; pdb.set_trace()
```

Or use your IDE's debugger (VS Code, PyCharm).

### View Logs

```bash
# Backend API logs
# Printed to stdout where uvicorn is running

# Celery worker logs
# Printed to stdout where celery worker is running

# View all Docker logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f worker
```

### Common Issues

#### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

#### Database Connection Errors

- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL environment variable
- Ensure database exists: `psql -l | grep adveritas`
- Verify pgvector extension: `psql adveritas -c "SELECT * FROM pg_extension WHERE extname='vector';"`

#### Celery Not Processing Tasks

- Ensure Redis is running: `redis-cli ping` (should return `PONG`)
- Check REDIS_URL environment variable
- Verify worker is running: `celery -A app.celery_app.celery_app inspect active`
- Check worker logs for errors

#### Model Download Issues

First-time use downloads large models (Whisper, embeddings):

- Whisper model (~3GB): Downloads to `~/.cache/huggingface/`
- Embedding model (~80MB): Downloads to `~/.cache/torch/`
- Ensure sufficient disk space and stable internet connection

## 📝 Project Structure

```
adveritas/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app initialization
│   │   ├── db.py                # Database configuration
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic validation schemas
│   │   ├── celery_app.py        # Celery configuration
│   │   │
│   │   ├── routers/             # API endpoints
│   │   │   ├── videos.py        # Video ingestion
│   │   │   ├── claims.py        # Claim extraction
│   │   │   ├── evidence.py      # Evidence retrieval
│   │   │   └── verdicts.py      # Verdict generation
│   │   │
│   │   ├── asr.py               # Speech-to-text (Whisper)
│   │   ├── claims_extract.py    # Claim extraction logic
│   │   ├── embeddings.py        # Vector embeddings
│   │   ├── evidence_retrieval.py # Web & Wikipedia search
│   │   ├── verdicts.py          # LLM verdict generation
│   │   ├── ingest.py            # Video download utilities
│   │   ├── storage.py           # S3/MinIO storage
│   │   │
│   │   ├── *_tasks.py           # Celery task definitions
│   │   │   ├── tasks.py         # Video processing pipeline
│   │   │   ├── claim_tasks.py   # Claim extraction tasks
│   │   │   ├── evidence_tasks.py # Evidence retrieval tasks
│   │   │   └── verdict_tasks.py  # Verdict generation tasks
│   │   │
│   │   └── alembic/             # Database migrations
│   │
│   ├── tests/                   # Test files
│   ├── Dockerfile
│   └── pyproject.toml           # Python dependencies
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx         # Main UI component
│   │       ├── layout.tsx       # App layout
│   │       └── globals.css      # Styles
│   ├── Dockerfile
│   └── package.json             # Node dependencies
│
├── docker-compose.yml           # Local development setup
├── README.md                    # Project overview
├── DEVELOPMENT.md               # This file
└── DEPLOYMENT_CHECKLIST.md      # Deployment guide
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Ensure all tests pass**: `pytest` and `npm test`
6. **Format your code**: `black .` and `npm run lint`
7. **Commit your changes**: `git commit -m 'Add amazing feature'`
8. **Push to your fork**: `git push origin feature/amazing-feature`
9. **Open a Pull Request**

### Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add Wikipedia search to evidence retrieval
fix: Correct verdict confidence calculation
docs: Update API documentation
test: Add tests for claim extraction
refactor: Simplify evidence ranking logic
```

### Pull Request Checklist

- [ ] Code follows project style (Black, ESLint)
- [ ] All tests pass
- [ ] New features include tests
- [ ] Documentation updated if needed
- [ ] No unnecessary dependencies added
- [ ] Commit messages are clear

## 🔗 Useful Commands

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload                    # Start API
celery -A app.celery_app.celery_app worker -l INFO  # Start worker
pytest                                            # Run tests
black .                                           # Format code
alembic upgrade head                              # Run migrations

# Frontend
cd frontend
npm run dev                                       # Start dev server
npm test                                          # Run tests
npm run lint                                      # Lint code
npm run build                                     # Production build

# Docker
docker-compose up -d                              # Start all services
docker-compose down                               # Stop all services
docker-compose logs -f                            # View logs
docker-compose restart api                        # Restart specific service

# Database
psql adveritas                                    # Connect to database
psql adveritas -c "\dt"                          # List tables
psql adveritas -c "SELECT * FROM videos;"        # Query videos

# Redis
redis-cli                                         # Connect to Redis
redis-cli PING                                    # Test Redis
redis-cli FLUSHALL                                # Clear all data (caution!)
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL pgvector](https://github.com/pgvector/pgvector)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

## 💬 Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check existing docs and API reference at `/docs`

---

Happy coding! 🚀

