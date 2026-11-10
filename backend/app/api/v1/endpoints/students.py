from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.student import Student
from app.models.face_embedding import FaceEmbedding
from app.models.class_section import ClassSection
from app.models.user import User, UserRole
from app.models.attendance import Attendance
from app.models.subject import Subject
from app.models.period import Period
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.api.deps import get_current_faculty_or_admin, get_current_active_admin, get_current_user

router = APIRouter()


@router.get("/portal/me")
def get_student_portal_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dedicated endpoint for students to view their own attendance metrics,
    subject-wise breakdown, eligibility, and period-wise attendance logs.
    """
    student = db.query(Student).filter(Student.email.ilike(current_user.email)).first()
    if not student:
        # If user is admin/faculty previewing portal, grab the first student as sample
        if current_user.role in (UserRole.ADMIN, UserRole.FACULTY):
            student = db.query(Student).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile associated with this account not found",
            )

    has_emb = db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student.id).count() > 0

    # Fetch all attendance records for this student
    records = (
        db.query(Attendance)
        .filter(Attendance.student_id == student.id)
        .order_by(desc(Attendance.date), desc(Attendance.period_id))
        .all()
    )

    total_classes = len(records)
    attended_classes = sum(1 for r in records if r.status in ("PRESENT", "LATE"))
    absent_classes = sum(1 for r in records if r.status == "ABSENT")
    attendance_pct = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 100.0
    is_eligible = attendance_pct >= 75.0

    # Subject-wise aggregation
    subjects = db.query(Subject).all()
    subject_map = {s.id: s for s in subjects}
    subject_stats = {}

    for r in records:
        sid = r.subject_id
        if sid not in subject_stats:
            sub = subject_map.get(sid)
            subject_stats[sid] = {
                "subject_id": sid,
                "name": sub.name if sub else f"Subject #{sid}",
                "code": sub.code if sub else f"SUB{sid}",
                "total": 0,
                "attended": 0,
                "absent": 0,
            }
        subject_stats[sid]["total"] += 1
        if r.status in ("PRESENT", "LATE"):
            subject_stats[sid]["attended"] += 1
        else:
            subject_stats[sid]["absent"] += 1

    subject_breakdown = []
    for sid, sdata in subject_stats.items():
        pct = round((sdata["attended"] / sdata["total"] * 100), 1) if sdata["total"] > 0 else 100.0
        subject_breakdown.append({
            **sdata,
            "percentage": pct,
            "status": "Safe" if pct >= 75.0 else "Shortage Warning",
        })

    # Detailed history logs (latest 50)
    history = []
    for r in records[:50]:
        sub = subject_map.get(r.subject_id)
        history.append({
            "id": r.id,
            "date": r.date.strftime("%Y-%m-%d"),
            "period_name": r.period.name if r.period else f"Period {r.period_id}",
            "period_number": r.period.period_number if r.period else r.period_id,
            "subject_name": sub.name if sub else "N/A",
            "subject_code": sub.code if sub else "N/A",
            "status": r.status,
            "confidence": round(r.confidence, 2) if r.confidence else None,
            "verification_method": r.verification_method,
            "timestamp": r.timestamp.strftime("%I:%M:%S %p") if r.timestamp else "",
        })

    return {
        "student": {
            "id": student.id,
            "reg_no": student.reg_no,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "full_name": student.full_name,
            "email": student.email,
            "class_section": student.class_section.name if student.class_section else "N/A",
            "department": student.class_section.department if student.class_section else "CSE",
            "semester": student.class_section.semester if student.class_section else 6,
            "has_face_registered": has_emb,
        },
        "metrics": {
            "total_classes": total_classes,
            "attended_classes": attended_classes,
            "absent_classes": absent_classes,
            "attendance_percentage": attendance_pct,
            "is_eligible": is_eligible,
            "threshold_required": 75.0,
            "status_label": "Eligible for End-Sem Examinations" if is_eligible else "Attendance Shortage (<75%)",
        },
        "subject_breakdown": subject_breakdown,
        "history": history,
    }


@router.get("/", response_model=List[StudentResponse])
def get_students(
    class_section_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    query = db.query(Student)
    if class_section_id:
        query = query.filter(Student.class_section_id == class_section_id)
    students = query.order_by(Student.reg_no.asc()).all()
    
    result = []
    for s in students:
        has_emb = db.query(FaceEmbedding).filter(FaceEmbedding.student_id == s.id).count() > 0
        s_dict = {
            "id": s.id,
            "reg_no": s.reg_no,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "full_name": s.full_name,
            "email": s.email,
            "class_section_id": s.class_section_id,
            "class_section": s.class_section,
            "consent_given": s.consent_given,
            "is_active": s.is_active,
            "created_at": s.created_at,
            "has_embeddings": has_emb,
        }
        result.append(s_dict)
    return result


@router.post("/", response_model=StudentResponse)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    # Verify class section exists
    sec = db.query(ClassSection).filter(ClassSection.id == student_in.class_section_id).first()
    if not sec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class section with ID {student_in.class_section_id} does not exist",
        )
    
    # Check registration number uniqueness
    existing_reg = db.query(Student).filter(Student.reg_no == student_in.reg_no).first()
    if existing_reg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with registration number '{student_in.reg_no}' already exists",
        )

    # Check email uniqueness
    existing_email = db.query(Student).filter(Student.email == student_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with email '{student_in.email}' already exists",
        )

    student = Student(**student_in.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)

    # Automatically create student login account
    existing_u = db.query(User).filter(User.email == student.email).first()
    if not existing_u:
        stu_user = User(
            email=student.email,
            hashed_password=get_password_hash("Student@123"),
            full_name=student.full_name,
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(stu_user)
        db.commit()

    return {
        "id": student.id,
        "reg_no": student.reg_no,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "full_name": student.full_name,
        "email": student.email,
        "class_section_id": student.class_section_id,
        "class_section": student.class_section,
        "consent_given": student.consent_given,
        "is_active": student.is_active,
        "created_at": student.created_at,
        "has_embeddings": False,
    }


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    has_emb = db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student.id).count() > 0
    return {
        "id": student.id,
        "reg_no": student.reg_no,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "full_name": student.full_name,
        "email": student.email,
        "class_section_id": student.class_section_id,
        "class_section": student.class_section,
        "consent_given": student.consent_given,
        "is_active": student.is_active,
        "created_at": student.created_at,
        "has_embeddings": has_emb,
    }


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    update_data = student_update.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(student, field, val)
    
    db.commit()
    db.refresh(student)
    
    has_emb = db.query(FaceEmbedding).filter(FaceEmbedding.student_id == student.id).count() > 0
    return {
        "id": student.id,
        "reg_no": student.reg_no,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "full_name": student.full_name,
        "email": student.email,
        "class_section_id": student.class_section_id,
        "class_section": student.class_section,
        "consent_given": student.consent_given,
        "is_active": student.is_active,
        "created_at": student.created_at,
        "has_embeddings": has_emb,
    }


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"message": f"Student {student.reg_no} deleted successfully"}
