from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.timetable import Timetable
from app.models.user import User
from app.schemas.timetable import TimetableCreate, TimetableResponse, ActivePeriodResponse
from app.services.timetable_service import get_current_period
from app.api.deps import get_current_faculty_or_admin, get_current_active_admin

router = APIRouter()


@router.get("/current", response_model=ActivePeriodResponse)
def check_current_period(
    class_section_id: Optional[int] = Query(None, description="Optional class section filter"),
    custom_time: Optional[str] = Query(None, description="ISO datetime string for simulation/testing e.g. 2026-11-04T09:15:00"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    """
    Returns the currently active period and timetable slot according to classroom schedule.
    """
    eval_time = datetime.now()
    if custom_time:
        try:
            eval_time = datetime.fromisoformat(custom_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ISO datetime format")

    period, slot, message = get_current_period(db, now=eval_time, class_section_id=class_section_id)

    return {
        "is_active": (period is not None and not period.is_break and slot is not None),
        "period": period,
        "timetable_slot": slot,
        "message": message,
    }


@router.get("/", response_model=List[TimetableResponse])
def get_timetables(
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    class_section_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    query = db.query(Timetable)
    if day_of_week is not None:
        query = query.filter(Timetable.day_of_week == day_of_week)
    if class_section_id is not None:
        query = query.filter(Timetable.class_section_id == class_section_id)
    return query.all()


@router.post("/", response_model=TimetableResponse)
def create_timetable_slot(
    tt_in: TimetableCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    # Check duplicate
    existing = db.query(Timetable).filter(
        Timetable.day_of_week == tt_in.day_of_week,
        Timetable.period_id == tt_in.period_id,
        Timetable.class_section_id == tt_in.class_section_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timetable slot conflict: Section already has a class in this period",
        )
    
    tt = Timetable(**tt_in.model_dump())
    db.add(tt)
    db.commit()
    db.refresh(tt)
    return tt


@router.delete("/{timetable_id}")
def delete_timetable_slot(
    timetable_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    tt = db.query(Timetable).filter(Timetable.id == timetable_id).first()
    if not tt:
        raise HTTPException(status_code=404, detail="Timetable slot not found")
    db.delete(tt)
    db.commit()
    return {"message": "Timetable slot deleted successfully"}
