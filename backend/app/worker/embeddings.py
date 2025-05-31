from celery import Celery
from backend.app.core.config import settings  # Adjust if config is elsewhere
from backend.app.db.session import get_db  # adjust if needed
from loguru import logger

# Celery app definition
celery_app = Celery(
    'embeddings',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task
def test_task(x, y):
    return x + y

@celery_app.task
def dummy_embedding_task():
    logger.info('Dummy embedding task executed')
    return 'ok'

# Add real embedding tasks here as needed 