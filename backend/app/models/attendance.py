from datetime import datetime, timezone, date as dt_date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, default=lambda: dt_date.today(), nullable=False, index=True)
    period_id = Column(Integer, ForeignKey("periods.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    class_section_id = Column(Integer, ForeignKey("class_sections.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String(20), default="PRESENT", nullable=False)  # "PRESENT", "ABSENT", "LATE"
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    confidence = Column(Float, nullable=True)                        # ML recognition confidence [0.0 - 1.0]
    verification_method = Column(String(50), default="FACE_RECOGNITION", nullable=False) # "FACE_RECOGNITION", "MANUAL"
    marked_by = Column(String(100), default="SYSTEM", nullable=False)

    __table_args__ = (
        # Crucial requirement: Exactly ONE attendance record per student per date per period
        UniqueConstraint("student_id", "date", "period_id", name="uq_student_date_period"),
    )

    student = relationship("Student", back_populates="attendances")
    period = relationship("Period", back_populates="attendances")
    subject = relationship("Subject", back_populates="attendances")
    class_section = relationship("ClassSection")
