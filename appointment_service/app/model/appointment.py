from datetime import datetime
from typing import List
from pydantic import BaseModel

class Appointment(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    slot_id: int
    success: bool = False
    remarks: str = None

    class Config:
        from_attributes = True
        validate_by_name = True
        arbitrary_types_allowed = True
   