from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class ClassSection(Base):
    __tablename__ = "class_sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "CSE-A", "CSE-B"
    department = Column(String(100), nullable=False)                    # e.g., "Computer Science & Engineering"
    academic_year = Column(String(20), nullable=False)                  # e.g., "2026-2027"
    semester = Column(Integer, nullable=False)                          # e.g., 6

    students = relationship("Student", back_populates="class_section", cascade="all, delete-orphan")
    timetables = relationship("Timetable", back_populates="class_section")
