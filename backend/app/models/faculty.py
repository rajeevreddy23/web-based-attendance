from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False, default="Assistant Professor")

    user = relationship("User")
    timetables = relationship("Timetable", back_populates="faculty")
