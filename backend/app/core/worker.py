from celery import Celery
from app.core.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    'markdown_converter',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['app.tasks.markdown_tasks']
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟任务超时
    task_soft_time_limit=25 * 60,  # 25分钟软超时
    result_expires=3600,  # 结果过期时间1小时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)