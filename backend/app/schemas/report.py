from typing import Optional
from datetime import date as dt_date
from pydantic import BaseModel


class ReportFilterRequest(BaseModel):
    start_date: dt_date
    end_date: dt_date
    class_section_id: Optional[int] = None
    subject_id: Optional[int] = None
    period_id: Optional[int] = None
    student_id: Optional[int] = None


class ReportDownloadResponse(BaseModel):
    filename: str
    download_url: str
    total_records: int
