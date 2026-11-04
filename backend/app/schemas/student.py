from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.schemas.class_section import ClassSectionResponse


class StudentBase(BaseModel):
    reg_no: str
    first_name: str
    last_name: str
    email: EmailStr
    class_section_id: int
    consent_given: bool = True
    is_active: bool = True


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    class_section_id: Optional[int] = None
    consent_given: Optional[bool] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    id: int
    full_name: str
    created_at: datetime
    class_section: Optional[ClassSectionResponse] = None
    has_embeddings: bool = False

    class Config:
        from_attributes = True


class FaceRegistrationRequest(BaseModel):
    student_id: int
    images_base64: List[str]  # 15-30 captured face images as Base64 strings
