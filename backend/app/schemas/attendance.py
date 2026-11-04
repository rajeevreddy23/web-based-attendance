from typing import Optional, List, Dict
from datetime import date as dt_date, datetime
from pydantic import BaseModel
from app.schemas.student import StudentResponse
from app.schemas.period import PeriodResponse
from app.schemas.subject import SubjectResponse


class AttendanceBase(BaseModel):
    student_id: int
    date: dt_date
    period_id: int
    subject_id: int
    class_section_id: int
    status: str = "PRESENT"
    confidence: Optional[float] = None
    verification_method: str = "FACE_RECOGNITION"
    marked_by: str = "SYSTEM"


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    timestamp: datetime
    student: Optional[StudentResponse] = None
    period: Optional[PeriodResponse] = None
    subject: Optional[SubjectResponse] = None

    class Config:
        from_attributes = True


class ManualCorrectionRequest(BaseModel):
    attendance_id: int
    new_status: str  # "PRESENT", "ABSENT", "LATE"
    reason: str


class LiveRecognitionEvent(BaseModel):
    student_id: int
    reg_no: str
    student_name: str
    class_section: str
    period_id: int
    period_name: str
    subject_code: str
    subject_name: str
    confidence: float
    timestamp: str
    status: str = "PRESENT"
