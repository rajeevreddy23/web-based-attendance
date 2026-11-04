from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    class_sections,
    subjects,
    periods,
    students,
    timetable,
    attendance,
    recognition,
    reports,
    ws,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(class_sections.router, prefix="/classes", tags=["Classes & Sections"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(periods.router, prefix="/periods", tags=["Periods"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(timetable.router, prefix="/timetable", tags=["Timetable"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(recognition.router, prefix="/recognition", tags=["Face Recognition & Vision"])
api_router.include_router(reports.router, prefix="/reports", tags=["Excel Reports"])
api_router.include_router(ws.router, prefix="/ws", tags=["Real-time WebSockets"])
