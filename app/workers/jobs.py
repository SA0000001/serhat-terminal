from app.ai_reports.reporter import AIReportGenerator
from app.workers.celery_app import celery_app


@celery_app.task
def generate_ai_report(payload: dict) -> str:
    reporter = AIReportGenerator()
    return reporter.generate_daily_report(payload)
