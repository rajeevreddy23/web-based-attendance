from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Timetable(Base):
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False, index=True)  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    period_id = Column(Integer, ForeignKey("periods.id", ondelete="CASCADE"), nullable=False)
    class_section_id = Column(Integer, ForeignKey("class_sections.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("faculty.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        UniqueConstraint("day_of_week", "period_id", "class_section_id", name="uq_day_period_class"),
    )

    period = relationship("Period", back_populates="timetables")
    class_section = relationship("ClassSection", back_populates="timetables")
    subject = relationship("Subject", back_populates="timetables")
    faculty = relationship("Faculty", back_populates="timetables")
