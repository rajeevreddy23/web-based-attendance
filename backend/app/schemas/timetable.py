from datetime import time
from typing import Optional
from pydantic import BaseModel
from app.schemas.subject import SubjectResponse
from app.schemas.class_section import ClassSectionResponse


class PeriodBase(BaseModel):
    period_number: int
    name: str
    start_time: time
    end_time: time
    is_break: bool = False


class PeriodCreate(PeriodBase):
    pass


class PeriodResponse(PeriodBase):
    id: int

    class Config:
        from_attributes = True


class TimetableBase(BaseModel):
    day_of_week: int
    period_id: int
    class_section_id: int
    subject_id: int
    faculty_id: Optional[int] = None


class TimetableCreate(TimetableBase):
    pass


class TimetableResponse(BaseModel):
    id: int
    day_of_week: int
    period: PeriodResponse
    class_section: ClassSectionResponse
    subject: SubjectResponse

    class Config:
        from_attributes = True


class ActivePeriodResponse(BaseModel):
    is_active: bool
    period: Optional[PeriodResponse] = None
    timetable_slot: Optional[TimetableResponse] = None
    message: str
