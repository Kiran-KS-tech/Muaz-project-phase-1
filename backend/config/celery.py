from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Celery Beat settings: Schedule periodic background tasks
app.conf.beat_schedule = {
    'check-document-expiries-every-midnight': {
        'task': 'apps.documents.tasks.check_document_expiries',
        # Run daily at midnight
        'schedule': crontab(hour=0, minute=0),
    },
    'generate-weekly-settlements-sunday': {
        'task': 'apps.settlements.tasks.generate_weekly_settlements',
        # Run every Sunday at midnight
        'schedule': crontab(day_of_week=0, hour=0, minute=0),
    },
    'send-scheduled-maintenance-alerts-daily': {
        'task': 'apps.cars.tasks.check_upcoming_maintenance',
        'schedule': crontab(hour=8, minute=0),  # Run every day at 8:00 AM
    },
}
