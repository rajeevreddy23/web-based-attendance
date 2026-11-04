from pydantic import BaseModel


class SubjectBase(BaseModel):
    code: str
    name: str
    department: str
    credits: int = 3


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True
