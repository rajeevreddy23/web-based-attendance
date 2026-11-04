import json
import logging
from datetime import datetime, date as dt_date, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.student import Student
from app.models.period import Period
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.models.audit_log import AuditLog
from app.services.timetable_service import get_current_period

logger = logging.getLogger(__name__)


def record_student_attendance(
    db: Session,
    student_id: int,
    confidence: float,
    now: Optional[datetime] = None,
    verification_method: str = "FACE_RECOGNITION",
    marked_by: str = "SYSTEM",
) -> Tuple[bool, Optional[Attendance], str]:
    """
    Core attendance recording logic.
    
    1. Verifies student exists and is active.
    2. Identifies current period from the timetable.
    3. Checks student belongs to the class section scheduled for this period.
    4. Checks if attendance already exists for (student_id, date, period_id).
    5. Inserts record (enforced in code AND by DB UniqueConstraint).
    """
    if now is None:
        now = datetime.now()
    
    record_date = now.date()

    # 1. Verify student exists and is active
    student = db.query(Student).filter(Student.id == student_id, Student.is_active == True).first()
    if not student:
        return False, None, f"Student ID {student_id} not found or inactive"

    # 2. Get active period and timetable slot for student's class
    period, slot, reason = get_current_period(db, now=now, class_section_id=student.class_section_id)
    if not period or not slot:
        return False, None, f"Attendance rejected: {reason}"

    # 3. Check section enrollment
    if student.class_section_id != slot.class_section_id:
        return False, None, f"Student {student.reg_no} is in section {student.class_section_id}, not scheduled section {slot.class_section_id}"

    # 4. Check duplicate in code
    existing = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.date == record_date,
        Attendance.period_id == period.id,
    ).first()

    if existing:
        return False, existing, f"Attendance already recorded for {student.full_name} ({student.reg_no}) in {period.name} at {existing.timestamp.strftime('%H:%M:%S')}"

    # Determine status (e.g. LATE if student arrives > 15 mins after period start)
    period_start_dt = datetime.combine(record_date, period.start_time)
    elapsed_minutes = (now - period_start_dt).total_seconds() / 60.0
    status = "LATE" if elapsed_minutes > 15.0 else "PRESENT"

    # 5. Insert record (protected by DB UniqueConstraint)
    attendance = Attendance(
        student_id=student.id,
        date=record_date,
        period_id=period.id,
        subject_id=slot.subject_id,
        class_section_id=slot.class_section_id,
        status=status,
        timestamp=now,
        confidence=confidence,
        verification_method=verification_method,
        marked_by=marked_by,
    )

    try:
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        logger.info(f"Marked {status} for student {student.reg_no} in period {period.period_number}")
        return True, attendance, f"Attendance successfully recorded: {student.full_name} ({student.reg_no}) marked {status}"
    except IntegrityError:
        db.rollback()
        # Concurrency race-condition handled by DB unique constraint
        existing_race = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == record_date,
            Attendance.period_id == period.id,
        ).first()
        return False, existing_race, f"Attendance already recorded (caught by DB UniqueConstraint) for {student.reg_no}"


def auto_mark_absent_for_period(
    db: Session,
    period_id: int,
    class_section_id: int,
    attendance_date: Optional[dt_date] = None,
) -> int:
    """
    At the end of a period, queries all enrolled students in the section who
    have NO attendance record for that date and period, and marks them ABSENT.
    """
    if attendance_date is None:
        attendance_date = dt_date.today()

    # Find the subject scheduled for this period & section
    day_of_week = attendance_date.weekday()
    slot = db.query(Timetable).filter(
        Timetable.day_of_week == day_of_week,
        Timetable.period_id == period_id,
        Timetable.class_section_id == class_section_id,
    ).first()

    if not slot:
        return 0

    # Get all active students in this class section
    enrolled_students = db.query(Student).filter(
        Student.class_section_id == class_section_id,
        Student.is_active == True,
    ).all()

    marked_absent_count = 0
    now_dt = datetime.now()

    for student in enrolled_students:
        exists = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == attendance_date,
            Attendance.period_id == period_id,
        ).first()

        if not exists:
            absent_record = Attendance(
                student_id=student.id,
                date=attendance_date,
                period_id=period_id,
                subject_id=slot.subject_id,
                class_section_id=class_section_id,
                status="ABSENT",
                timestamp=now_dt,
                confidence=None,
                verification_method="AUTOMATED_PERIOD_END",
                marked_by="SCHEDULER",
            )
            try:
                db.add(absent_record)
                db.commit()
                marked_absent_count += 1
            except IntegrityError:
                db.rollback()

    return marked_absent_count


def apply_manual_correction(
    db: Session,
    attendance_id: int,
    new_status: str,
    faculty_email: str,
    reason: str,
) -> Tuple[bool, Optional[Attendance], str]:
    """
    Allows authorized faculty or admin to correct attendance status,
    creating an audit trail log in the audit_logs table.
    """
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        return False, None, "Attendance record not found"

    old_status = record.status
    record.status = new_status
    record.verification_method = "MANUAL"
    record.marked_by = faculty_email

    # Create audit log entry
    audit = AuditLog(
        entity_name="Attendance",
        entity_id=record.id,
        action="MANUAL_CORRECTION",
        old_values=json.dumps({"status": old_status}),
        new_values=json.dumps({"status": new_status}),
        performed_by=faculty_email,
        reason=reason,
    )
    db.add(audit)
    db.commit()
    db.refresh(record)
    return True, record, f"Attendance status updated from {old_status} to {new_status}"
