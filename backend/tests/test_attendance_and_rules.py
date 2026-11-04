import os
import sys
import pytest
from datetime import datetime, date as dt_date, time, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.core.database import Base
from app.models.user import User, UserRole
from app.models.class_section import ClassSection
from app.models.subject import Subject
from app.models.period import Period
from app.models.student import Student
from app.models.timetable import Timetable
from app.models.attendance import Attendance
from app.models.audit_log import AuditLog
from app.services.timetable_service import get_current_period
from app.services.attendance_service import (
    record_student_attendance,
    auto_mark_absent_for_period,
    apply_manual_correction,
)

# Test SQLite in-memory database
TEST_DB_URL = "sqlite:///:memory:"
engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    
    # Setup test entities
    sec_a = ClassSection(name="TEST-CSE-A", department="CSE", academic_year="2026", semester=6)
    sec_b = ClassSection(name="TEST-CSE-B", department="CSE", academic_year="2026", semester=6)
    db.add_all([sec_a, sec_b])
    db.commit()

    sub_ml = Subject(code="T-CS601", name="Machine Learning", department="CSE", credits=4)
    sub_cc = Subject(code="T-CS602", name="Cloud Computing", department="CSE", credits=3)
    db.add_all([sub_ml, sub_cc])
    db.commit()

    # Periods: P1 (09:00 - 09:50), P2 (09:50 - 10:40), Break (10:40 - 10:55)
    p1 = Period(period_number=1, name="Period 1", start_time=time(9, 0), end_time=time(9, 50), is_break=False)
    p2 = Period(period_number=2, name="Period 2", start_time=time(9, 50), end_time=time(10, 40), is_break=False)
    p_brk = Period(period_number=3, name="Tea Break", start_time=time(10, 40), end_time=time(10, 55), is_break=True)
    db.add_all([p1, p2, p_brk])
    db.commit()

    # Students
    st1 = Student(reg_no="T001", first_name="Alice", last_name="Smith", email="alice@test.edu", class_section_id=sec_a.id)
    st2 = Student(reg_no="T002", first_name="Bob", last_name="Jones", email="bob@test.edu", class_section_id=sec_a.id)
    st_b = Student(reg_no="T003", first_name="Charlie", last_name="Brown", email="charlie@test.edu", class_section_id=sec_b.id)
    db.add_all([st1, st2, st_b])
    db.commit()

    # Timetable for Monday (day 0):
    # Period 1: Sec A has Machine Learning
    # Period 2: Sec A has Cloud Computing
    tt1 = Timetable(day_of_week=0, period_id=p1.id, class_section_id=sec_a.id, subject_id=sub_ml.id)
    tt2 = Timetable(day_of_week=0, period_id=p2.id, class_section_id=sec_a.id, subject_id=sub_cc.id)
    db.add_all([tt1, tt2])
    db.commit()

    yield db
    db.close()
    Base.metadata.drop_all(bind=engine_test)


def test_timetable_active_period_evaluation(db_session):
    """Test get_current_period during active class, during break, and on Sunday."""
    # Monday at 09:15 -> Should return Period 1 with ML
    mon_p1_time = datetime(2026, 11, 2, 9, 15, 0)  # 2026-11-02 is Monday
    period, slot, reason = get_current_period(db_session, now=mon_p1_time, class_section_id=1)
    assert period is not None
    assert period.period_number == 1
    assert slot is not None
    assert slot.subject.code == "T-CS601"

    # Monday at 10:45 -> During break
    mon_brk_time = datetime(2026, 11, 2, 10, 45, 0)
    period_b, slot_b, reason_b = get_current_period(db_session, now=mon_brk_time, class_section_id=1)
    assert period_b is not None
    assert period_b.is_break is True
    assert slot_b is None

    # Sunday -> Should return None
    sun_time = datetime(2026, 11, 8, 9, 15, 0)  # 2026-11-08 is Sunday
    period_s, slot_s, reason_s = get_current_period(db_session, now=sun_time, class_section_id=1)
    assert period_s is None
    assert "Sunday" in reason_s


def test_attendance_marking_and_duplicate_prevention(db_session):
    """Test attendance recording and verify duplicate detection within the same period."""
    st1 = db_session.query(Student).filter(Student.reg_no == "T001").first()
    mon_p1_time = datetime(2026, 11, 2, 9, 5, 0)

    # 1. First recognition in Period 1
    success, record, msg = record_student_attendance(
        db_session, student_id=st1.id, confidence=0.98, now=mon_p1_time
    )
    assert success is True
    assert record is not None
    assert record.status == "PRESENT"
    assert record.subject.code == "T-CS601"

    # Verify only 1 record exists in DB
    total_records = db_session.query(Attendance).count()
    assert total_records == 1

    # 2. Second recognition of same student in same period (e.g. 10 minutes later)
    repeat_time = datetime(2026, 11, 2, 9, 15, 0)
    success_2, record_2, msg_2 = record_student_attendance(
        db_session, student_id=st1.id, confidence=0.97, now=repeat_time
    )
    assert success_2 is False
    assert "Attendance already recorded" in msg_2
    assert record_2.id == record.id

    # Still exactly 1 record in DB (Duplicate prevented!)
    assert db_session.query(Attendance).count() == 1


def test_database_unique_constraint_enforcement(db_session):
    """Verify that the database UNIQUE constraint uq_student_date_period prevents duplicate insert."""
    st1 = db_session.query(Student).filter(Student.reg_no == "T001").first()
    p1 = db_session.query(Period).filter(Period.period_number == 1).first()
    sub = db_session.query(Subject).first()
    sec = db_session.query(ClassSection).first()

    rec1 = Attendance(
        student_id=st1.id,
        date=dt_date(2026, 11, 2),
        period_id=p1.id,
        subject_id=sub.id,
        class_section_id=sec.id,
        status="PRESENT",
        timestamp=datetime.now(),
    )
    db_session.add(rec1)
    db_session.commit()

    # Attempt to bypass application logic and insert duplicate directly into table
    rec2 = Attendance(
        student_id=st1.id,
        date=dt_date(2026, 11, 2),
        period_id=p1.id,
        subject_id=sub.id,
        class_section_id=sec.id,
        status="PRESENT",
        timestamp=datetime.now(),
    )
    db_session.add(rec2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_period_transition_different_periods_allowed(db_session):
    """Verify the student receives distinct attendance records for Period 1 and Period 2."""
    st1 = db_session.query(Student).filter(Student.reg_no == "T001").first()
    
    # Period 1 (09:00 - 09:50) -> Machine Learning
    p1_time = datetime(2026, 11, 2, 9, 10, 0)
    s1, r1, m1 = record_student_attendance(db_session, student_id=st1.id, confidence=0.96, now=p1_time)
    assert s1 is True
    assert r1.subject.code == "T-CS601"

    # Period 2 (09:50 - 10:40) -> Cloud Computing
    p2_time = datetime(2026, 11, 2, 10, 0, 0)
    s2, r2, m2 = record_student_attendance(db_session, student_id=st1.id, confidence=0.94, now=p2_time)
    assert s2 is True
    assert r2.subject.code == "T-CS602"

    # Both records must coexist in database
    records = db_session.query(Attendance).filter(Attendance.student_id == st1.id).all()
    assert len(records) == 2
    period_numbers = [r.period.period_number for r in records]
    assert 1 in period_numbers
    assert 2 in period_numbers


def test_section_mismatch_rejection(db_session):
    """Verify a student from Section B is rejected if Section A is scheduled."""
    st_b = db_session.query(Student).filter(Student.reg_no == "T003").first()
    p1_time = datetime(2026, 11, 2, 9, 10, 0)

    success, record, msg = record_student_attendance(db_session, student_id=st_b.id, confidence=0.95, now=p1_time)
    assert success is False
    assert "not scheduled" in msg or "rejected" in msg.lower()


def test_automated_absent_handling(db_session):
    """Verify students with no attendance in the period are marked ABSENT at period end."""
    st1 = db_session.query(Student).filter(Student.reg_no == "T001").first()
    p1 = db_session.query(Period).filter(Period.period_number == 1).first()
    sec_a = db_session.query(ClassSection).filter(ClassSection.name == "TEST-CSE-A").first()

    # Only st1 is marked PRESENT in Period 1
    p1_time = datetime(2026, 11, 2, 9, 10, 0)
    record_student_attendance(db_session, student_id=st1.id, confidence=0.96, now=p1_time)

    # Trigger period end auto-absent job for Section A
    marked_count = auto_mark_absent_for_period(
        db_session,
        period_id=p1.id,
        class_section_id=sec_a.id,
        attendance_date=dt_date(2026, 11, 2),
    )
    # st2 was enrolled in sec_a but had no record -> should be marked ABSENT
    assert marked_count == 1

    st2 = db_session.query(Student).filter(Student.reg_no == "T002").first()
    st2_record = db_session.query(Attendance).filter(
        Attendance.student_id == st2.id,
        Attendance.period_id == p1.id,
    ).first()
    assert st2_record is not None
    assert st2_record.status == "ABSENT"


def test_manual_correction_and_audit_trail(db_session):
    """Verify faculty manual status correction creates a traceable audit log entry."""
    st1 = db_session.query(Student).filter(Student.reg_no == "T001").first()
    p1_time = datetime(2026, 11, 2, 9, 10, 0)
    _, record, _ = record_student_attendance(db_session, student_id=st1.id, confidence=0.96, now=p1_time)

    # Faculty overrides status to LATE
    success, updated, msg = apply_manual_correction(
        db_session,
        attendance_id=record.id,
        new_status="LATE",
        faculty_email="prof.sharma@college.edu",
        reason="Student had laboratory permission slip",
    )
    assert success is True
    assert updated.status == "LATE"

    # Check audit_logs table
    audit = db_session.query(AuditLog).filter(AuditLog.entity_id == record.id).first()
    assert audit is not None
    assert audit.performed_by == "prof.sharma@college.edu"
    assert "permission slip" in audit.reason
    assert "PRESENT" in audit.old_values
    assert "LATE" in audit.new_values
