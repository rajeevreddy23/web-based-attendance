from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.class_section import ClassSection
from app.models.user import User
from app.schemas.class_section import ClassSectionCreate, ClassSectionResponse
from app.api.deps import get_current_faculty_or_admin, get_current_active_admin

router = APIRouter()


@router.get("/", response_model=List[ClassSectionResponse])
def get_class_sections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return db.query(ClassSection).all()


@router.post("/", response_model=ClassSectionResponse)
def create_class_section(
    sec_in: ClassSectionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    existing = db.query(ClassSection).filter(ClassSection.name == sec_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Class section '{sec_in.name}' already exists",
        )
    sec = ClassSection(**sec_in.model_dump())
    db.add(sec)
    db.commit()
    db.refresh(sec)
    return sec
