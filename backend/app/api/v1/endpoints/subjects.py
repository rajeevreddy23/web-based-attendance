from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.subject import Subject
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectResponse
from app.api.deps import get_current_faculty_or_admin, get_current_active_admin

router = APIRouter()


@router.get("/", response_model=List[SubjectResponse])
def get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return db.query(Subject).all()


@router.post("/", response_model=SubjectResponse)
def create_subject(
    sub_in: SubjectCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    existing = db.query(Subject).filter(Subject.code == sub_in.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject with code '{sub_in.code}' already exists",
        )
    subject = Subject(**sub_in.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject
