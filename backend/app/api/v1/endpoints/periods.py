from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.period import Period
from app.models.user import User
from app.schemas.period import PeriodCreate, PeriodResponse
from app.api.deps import get_current_faculty_or_admin, get_current_active_admin

router = APIRouter()


@router.get("/", response_model=List[PeriodResponse])
def get_periods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return db.query(Period).order_by(Period.period_number.asc()).all()


@router.post("/", response_model=PeriodResponse)
def create_period(
    period_in: PeriodCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    existing = db.query(Period).filter(Period.period_number == period_in.period_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Period number {period_in.period_number} already exists",
        )
    p = Period(**period_in.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p
