from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(50), nullable=False, index=True)    # e.g., "Attendance", "Student", "Timetable"
    entity_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)                     # "CREATE", "UPDATE", "DELETE", "MANUAL_CORRECTION"
    old_values = Column(Text, nullable=True)                       # JSON snapshot before modification
    new_values = Column(Text, nullable=True)                       # JSON snapshot after modification
    performed_by = Column(String(255), nullable=False)             # Email of faculty or admin
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reason = Column(String(255), nullable=True)                    # Reason given for manual correction
