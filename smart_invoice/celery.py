"""Celery configuration for Smart Invoice.

Optional async task queue for email sending, PDF generation, and background jobs.
Currently using ThreadPoolExecutor but can upgrade to Celery + Redis for production.
"""
import os
from celery import Celery  # type: ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_invoice.settings')

app = Celery('smart_invoice')  # type: ignore
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)  # type: ignore
def debug_task(self):  # type: ignore
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
