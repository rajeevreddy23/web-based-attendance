from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    reg_no = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "21CS001"
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    class_section_id = Column(Integer, ForeignKey("class_sections.id", ondelete="CASCADE"), nullable=False)
    consent_given = Column(Boolean, default=True, nullable=False)          # Ethical biometric consent flag
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    class_section = relationship("ClassSection", back_populates="students")
    face_embeddings = relationship("FaceEmbedding", back_populates="student", cascade="all, delete-orphan")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
