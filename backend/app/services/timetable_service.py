from datetime import datetime, time
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.period import Period
from app.models.timetable import Timetable
from app.models.class_section import ClassSection


def get_current_period(
    db: Session,
    now: Optional[datetime] = None,
    class_section_id: Optional[int] = None,
) -> Tuple[Optional[Period], Optional[Timetable], str]:
    """
    Evaluates the active period and timetable slot for the current moment or given datetime.
    
    Returns:
        (Period or None, Timetable or None, reason_message)
    """
    if now is None:
        now = datetime.now()
    
    # 0 = Monday, ..., 6 = Sunday
    day_of_week = now.weekday()
    current_time = now.time()

    # Sunday is off
    if day_of_week == 6:
        return None, None, "Sunday - No scheduled classes today"

    # Find the period spanning current_time
    period = db.query(Period).filter(
        Period.start_time <= current_time,
        Period.end_time >= current_time,
    ).first()

    if not period:
        # Check if before college hours or after
        earliest = db.query(Period).order_by(Period.start_time.asc()).first()
        latest = db.query(Period).order_by(Period.end_time.desc()).first()
        
        if earliest and current_time < earliest.start_time:
            return None, None, f"College has not started yet (First period starts at {earliest.start_time.strftime('%H:%M')})"
        elif latest and current_time > latest.end_time:
            return None, None, f"Classes ended for today (Last period ended at {latest.end_time.strftime('%H:%M')})"
        return None, None, "Passing period / Interval between classes"

    if period.is_break:
        return period, None, f"{period.name} in progress (No attendance taken during breaks)"

    # Now look up the active subject slot in the timetable
    tt_query = db.query(Timetable).filter(
        Timetable.day_of_week == day_of_week,
        Timetable.period_id == period.id,
    )
    if class_section_id:
        tt_query = tt_query.filter(Timetable.class_section_id == class_section_id)
    
    timetable_slot = tt_query.first()
    if not timetable_slot:
        return period, None, f"{period.name} is active, but no subject scheduled for this section today"

    return period, timetable_slot, f"Active Period: {period.name} - Subject: {timetable_slot.subject.name} ({timetable_slot.subject.code})"
