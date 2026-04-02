from celery import Celery

from app.config.settings import AppSettings

settings = AppSettings()
celery_app = Celery("trading_platform", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_routes = {
    "app.workers.jobs.generate_ai_report": {"queue": "reports"},
}
