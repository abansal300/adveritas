FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir uv

# Using pip since pyproject is minimal; you can switch to pdm/uv/poetry later
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn[standard]==0.30.6 \
    pydantic==2.9.2 SQLAlchemy==2.0.35 psycopg[binary]==3.2.3 alembic==1.13.2 \
    redis==5.0.8 celery==5.4.0 boto3==1.35.36 python-multipart==0.0.12 httpx==0.27.2

COPY app ./app
EXPOSE 8000
