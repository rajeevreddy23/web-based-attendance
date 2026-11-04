from datetime import time
from pydantic import BaseModel


class PeriodBase(BaseModel):
    period_number: int
    name: str
    start_time: time
    end_time: time
    is_break: bool = False


class PeriodCreate(PeriodBase):
    pass


class PeriodResponse(PeriodBase):
    id: int

    class Config:
        from_attributes = True
