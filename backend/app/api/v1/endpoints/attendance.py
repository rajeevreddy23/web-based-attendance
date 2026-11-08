from typing import List, Optional, Dict, Any
from datetime import date as dt_date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.subject import Subject
from app.models.period import Period
from app.models.class_section import ClassSection
from app.models.user import User
from app.schemas.attendance import AttendanceResponse, AttendanceCreate, ManualCorrectionRequest
from app.services.attendance_service import (
    record_student_attendance,
    apply_manual_correction,
    auto_mark_absent_for_period,
)
from app.api.deps import get_current_faculty_or_admin
from app.api.v1.endpoints.ws import ws_manager

router = APIRouter()


@router.get("/", response_model=List[AttendanceResponse])
def get_attendance(
    attendance_date: Optional[dt_date] = Query(None, alias="date"),
    class_section_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    period_id: Optional[int] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    query = db.query(Attendance)
    if attendance_date:
        query = query.filter(Attendance.date == attendance_date)
    if class_section_id:
        query = query.filter(Attendance.class_section_id == class_section_id)
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)
    if period_id:
        query = query.filter(Attendance.period_id == period_id)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    records = query.order_by(Attendance.timestamp.desc()).all()
    return records


@router.post("/record")
async def record_attendance_manually(
    student_id: int = Query(...),
    confidence: float = Query(0.95),
    period_id: Optional[int] = Query(None),
    simulated_time: Optional[str] = Query(None, description="ISO datetime for backfill/testing e.g. 2026-11-04T09:15:00"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    eval_time = datetime.now()
    if simulated_time:
        try:
            eval_time = datetime.fromisoformat(simulated_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ISO datetime")

    success, record, message = record_student_attendance(
        db,
        student_id=student_id,
        confidence=confidence,
        now=eval_time,
        verification_method="MANUAL_OVERRIDE",
        marked_by=current_user.email,
        period_id=period_id,
    )

    st = db.query(Student).filter(Student.id == student_id).first()
    if st:
        await ws_manager.broadcast_event({
            "student_id": st.id,
            "reg_no": st.reg_no,
            "student_name": st.full_name,
            "confidence": confidence,
            "time": datetime.now().strftime("%I:%M:%S %p"),
            "status": record.status if record else "ALREADY_RECORDED",
            "period_name": record.period.name if record and record.period else "Class Period",
            "subject_code": record.subject.code if record and record.subject else "CS601",
        })

    if not success:
        return {"success": False, "message": message, "record": record}
    return {"success": True, "message": message, "record_id": record.id}


@router.post("/correction")
def correct_attendance(
    correction: ManualCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    success, record, message = apply_manual_correction(
        db,
        attendance_id=correction.attendance_id,
        new_status=correction.new_status,
        faculty_email=current_user.email,
        reason=correction.reason,
    )
    if not success:
        raise HTTPException(status_code=404, detail=message)
    return {"success": True, "message": message, "new_status": record.status}


@router.post("/auto-absent")
def trigger_auto_absent(
    period_id: int = Query(...),
    class_section_id: int = Query(...),
    attendance_date: Optional[dt_date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    count = auto_mark_absent_for_period(
        db,
        period_id=period_id,
        class_section_id=class_section_id,
        attendance_date=attendance_date,
    )
    return {"message": f"Successfully marked {count} unrecorded students as ABSENT for period {period_id}", "marked_count": count}


@router.get("/stats")
def get_attendance_statistics(
    class_section_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    query = db.query(Attendance)
    if class_section_id:
        query = query.filter(Attendance.class_section_id == class_section_id)

    total_records = query.count()
    present_count = query.filter(Attendance.status.in_(["PRESENT", "LATE"])).count()
    absent_count = query.filter(Attendance.status == "ABSENT").count()
    late_count = query.filter(Attendance.status == "LATE").count()

    overall_percentage = round((present_count / total_records * 100), 2) if total_records > 0 else 0.0

    # Subject-wise stats
    subjects = db.query(Subject).all()
    subject_stats = []
    for sub in subjects:
        sub_total = db.query(Attendance).filter(Attendance.subject_id == sub.id).count()
        sub_present = db.query(Attendance).filter(
            Attendance.subject_id == sub.id,
            Attendance.status.in_(["PRESENT", "LATE"])
        ).count()
        pct = round((sub_present / sub_total * 100), 2) if sub_total > 0 else 0.0
        subject_stats.append({
            "subject_code": sub.code,
            "subject_name": sub.name,
            "total_classes": sub_total,
            "present_count": sub_present,
            "percentage": pct,
        })

    # Top student stats
    students = db.query(Student).limit(10).all()
    student_stats = []
    for st in students:
        st_total = db.query(Attendance).filter(Attendance.student_id == st.id).count()
        st_present = db.query(Attendance).filter(
            Attendance.student_id == st.id,
            Attendance.status.in_(["PRESENT", "LATE"])
        ).count()
        pct = round((st_present / st_total * 100), 2) if st_total > 0 else 0.0
        student_stats.append({
            "student_id": st.id,
            "reg_no": st.reg_no,
            "name": st.full_name,
            "total_periods": st_total,
            "present_periods": st_present,
            "percentage": pct,
        })

    return {
        "total_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "overall_percentage": overall_percentage,
        "subject_stats": subject_stats,
        "student_stats": student_stats,
    }
