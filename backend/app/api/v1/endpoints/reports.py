import os
from datetime import date as dt_date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.services.report_service import generate_attendance_excel
from app.schemas.report import ReportDownloadResponse
from app.api.deps import get_current_faculty_or_admin

router = APIRouter()


@router.post("/generate", response_model=ReportDownloadResponse)
def create_report(
    start_date: dt_date = Query(...),
    end_date: dt_date = Query(...),
    class_section_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    period_id: Optional[int] = None,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    """Generates an Excel spreadsheet (.xlsx) for the requested criteria."""
    try:
        filepath = generate_attendance_excel(
            db=db,
            start_date=start_date,
            end_date=end_date,
            class_section_id=class_section_id,
            subject_id=subject_id,
            period_id=period_id,
            student_id=student_id,
        )
        filename = os.path.basename(filepath)
        return {
            "filename": filename,
            "download_url": f"/api/v1/reports/download/{filename}",
            "total_records": 1,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/download/{filename}")
def download_report(
    filename: str,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: None),
):
    """Serves the generated Excel report file for download with token or header support."""
    filepath = os.path.join(settings.REPORTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Requested report file not found")

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
