from datetime import date, time
from typing import List
from pydantic import BaseModel

class Slot(BaseModel):
    slot_id: int
    doctor_id: int
    date: date
    time: time


    class Config:
        from_attributes = True
        validate_by_name = True
        arbitrary_types_allowed = True