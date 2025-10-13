import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Single app that imports all task modules
celery_app = Celery(
    "adveritas",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks",           # ASR pipeline tasks
        "app.claim_tasks",     # claim extraction tasks
        "app.evidence_tasks",  # evidence fetch tasks
        "app.verdict_tasks",   # verdict generation tasks
    ],
)

# sensible defaults
celery_app.conf.update(
    task_default_queue="celery",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
