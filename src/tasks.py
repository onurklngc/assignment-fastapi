import os
import time
from datetime import datetime

from celery.utils.log import get_task_logger

from celery_app import app
from src.database_config import DatabaseConfig
from src.model import Book

logger = get_task_logger(__name__)
database_url = os.getenv("DATABASE_URL")
database_config = None

while True:
    try:
        database_config = DatabaseConfig(database_url=database_url)
        break
    except Exception as e:
        logger.error(f"Couldn't connect to DB: {e}, will try again shortly after.")
        time.sleep(2)


@app.task
def send_overdue_reminders():
    logger.info("Sending overdue reminders")
    now = datetime.utcnow()
    db = next(database_config.get_db())
    overdue_books = db.query(Book).filter(Book.due_date < now, Book.is_checked_out).all()

    for book in overdue_books:
        patron = book.patron
        send_email(patron.email, "Overdue Book Reminder", f"Your book '{book.title}' is overdue.")


@app.task
def generate_weekly_reports():
    logger.info("Generating weekly reports")
    now = datetime.utcnow()
    db = next(database_config.get_db())

    books_count = db.query(Book).count()
    books_in_library_count = db.query(Book).filter(~Book.is_checked_out).count()
    books_with_overdue_count = db.query(Book).filter(Book.is_checked_out, Book.due_date < now).count()
    report = f"[ In library: {books_in_library_count} | All:{books_count} | " \
             f"With overdue: {books_with_overdue_count}"
    logger.info(f"Weekly book report: {report} ]")
    # Generate and save the report
    with open("weekly_report.txt", "a+") as report_file:
        report_file.write(f"\n{datetime.now()} - {report}")


def send_email(to, subject, body):
    # Email sending logic here
    logger.info(f"Sending email to {to} with subject '{subject}' and body '{body}'")


if __name__ == '__main__':
    import logging
    import src.config as cfg

    logging.basicConfig(level=getattr(logging, cfg.LOG_LEVEL), format=cfg.LOGGING_FORMAT, datefmt=cfg.TIME_FORMAT)
    generate_weekly_reports.apply()
    send_overdue_reminders.apply()
    send_email("1", "2", "3")
