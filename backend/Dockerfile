FROM python:3.11-slim

# --- system deps for audio/ffmpeg ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
    fastapi==0.115.0 uvicorn[standard]==0.30.6 pydantic==2.9.2 \
    SQLAlchemy==2.0.35 psycopg[binary]==3.2.3 alembic==1.13.2 \
    redis==5.0.8 celery==5.4.0 boto3==1.35.36 python-multipart==0.0.12 httpx==0.27.2 \
    fastapi-cors==0.0.6 pgvector==0.2.5 \
    yt-dlp==2024.10.7 \
    sentence-transformers==3.1.1 \
    wikipedia==1.4.0 \
    requests==2.32.3 \
    faster-whisper==1.1.0 soundfile==0.12.1 numpy==1.26.4

# NLP / HF - install torch first with CPU support, then other packages
RUN pip install --no-cache-dir torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir \
    transformers==4.44.2 \
    nltk==3.9.1 

RUN pip install --no-cache-dir json5==0.9.25

# Pre-download NLTK tokenizers so workers don't fetch at runtime
RUN python - <<'PY'
import nltk
nltk.download('punkt')
try:
    nltk.download('punkt_tab')
except Exception:
    pass
PY



# Copy the whole backend so alembic/app code is available
COPY . .
EXPOSE 8000
