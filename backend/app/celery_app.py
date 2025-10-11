import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("adveritas", broker=redis_url, backend=redis_url)

@celery_app.task(name="ping")
def ping():
    return "pong"
