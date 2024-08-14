import os

from celery import Celery
from celery.schedules import crontab

celery_broker_url = os.getenv("CELERY_BROKER_URL")
celery_result_backend = os.getenv("CELERY_RESULT_BACKEND")
overdue_reminder_hour = os.getenv("OVERDUE_REMINDER_HOUR", '6')
generating_report_hour = os.getenv("GENERATING_REPORT_HOUR", '17')
generating_report_minute = os.getenv("GENERATING_REPORT_MINUTE", '5')

app = Celery("library_tasks", broker=celery_broker_url, backend=celery_result_backend,
             include=["src.tasks"])

app.conf.update(
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        # Daily task for overdue reminders
        'send-overdue-reminders': {
            'task': 'src.tasks.send_overdue_reminders',
            'schedule': crontab(hour=overdue_reminder_hour, minute='0'),
            # 'schedule': crontab(minute="*"),
        },
        # Weekly task for generating reports
        'generate-weekly-reports': {
            'task': 'src.tasks.generate_weekly_reports',
            'schedule': crontab(hour=generating_report_hour, minute='30', day_of_week='6'),
            # 'schedule': crontab(minute="*"),
        },
    },
)
