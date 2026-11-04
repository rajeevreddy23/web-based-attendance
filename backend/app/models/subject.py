from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # e.g., "CS601"
    name = Column(String(100), nullable=False)                         # e.g., "Machine Learning"
    department = Column(String(100), nullable=False)
    credits = Column(Integer, default=3, nullable=False)

    timetables = relationship("Timetable", back_populates="subject")
    attendances = relationship("Attendance", back_populates="subject")
