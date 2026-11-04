from pydantic import BaseModel


class ClassSectionBase(BaseModel):
    name: str
    department: str
    academic_year: str
    semester: int


class ClassSectionCreate(ClassSectionBase):
    pass


class ClassSectionResponse(ClassSectionBase):
    id: int

    class Config:
        from_attributes = True
