import logging
from datetime import datetime, date as dt_date
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.period import Period
from app.models.class_section import ClassSection
from app.services.attendance_service import auto_mark_absent_for_period
from app.services.report_service import generate_attendance_excel

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def period_end_absent_job():
    """
    Runs every minute: checks if current time aligns with the end of any period.
    If so, automatically marks unrecorded students as ABSENT.
    """
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")

    db: Session = SessionLocal()
    try:
        periods = db.query(Period).filter(Period.is_break == False).all()
        sections = db.query(ClassSection).all()

        for p in periods:
            period_end_str = p.end_time.strftime("%H:%M")
            if current_time_str == period_end_str:
                logger.info(f"Triggering Auto-Absent evaluation for {p.name} (End time: {period_end_str})")
                for sec in sections:
                    count = auto_mark_absent_for_period(
                        db,
                        period_id=p.id,
                        class_section_id=sec.id,
                        attendance_date=now.date(),
                    )
                    if count > 0:
                        logger.info(f"Marked {count} students ABSENT in section {sec.name} for {p.name}")
    except Exception as e:
        logger.error(f"Error in period_end_absent_job: {e}")
    finally:
        db.close()


def daily_report_job():
    """Scheduled job that compiles the end-of-day attendance report."""
    now = datetime.now()
    db: Session = SessionLocal()
    try:
        report_path = generate_attendance_excel(
            db,
            start_date=now.date(),
            end_date=now.date(),
        )
        logger.info(f"Daily automated attendance report generated: {report_path}")
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
    finally:
        db.close()


def start_scheduler():
    """Starts background APScheduler tasks."""
    if not scheduler.running:
        scheduler.add_job(period_end_absent_job, "cron", second=0, id="auto_absent_checker", replace_existing=True)
        scheduler.add_job(daily_report_job, "cron", hour=17, minute=30, id="daily_report_task", replace_existing=True)
        scheduler.start()
        logger.info("APScheduler background service started successfully")


def stop_scheduler():
    """Stops background APScheduler tasks."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler service stopped")
