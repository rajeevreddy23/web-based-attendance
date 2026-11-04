from sqlalchemy import Column, Integer, String, Time, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, index=True)
    period_number = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String(50), nullable=False)           # e.g., "Period 1 (09:00 - 09:50)"
    start_time = Column(Time, nullable=False)          # e.g., 09:00:00
    end_time = Column(Time, nullable=False)            # e.g., 09:50:00
    is_break = Column(Boolean, default=False, nullable=False)

    timetables = relationship("Timetable", back_populates="period")
    attendances = relationship("Attendance", back_populates="period")
