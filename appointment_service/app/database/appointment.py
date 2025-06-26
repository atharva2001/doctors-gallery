from app.database.core import Base 
from sqlalchemy import TIMESTAMP, Column, String, Boolean, Integer
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE


class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False, index=True)
    doctor_id = Column(Integer, nullable=False, index=True)
    slot_id = Column(Integer, nullable=False)
    success = Column(Boolean, default=False)
    remarks = Column(String(500), nullable=True)



def get_all_appointments(db):
    results = db.query(Appointment).all()
    return results if results else []

def get_appointment_by_patient_id(db, patient_id: int):
    results = db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
    return results if results else []

def get_appointment_by_doctor_id(db, doctor_id: int):
    results = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()
    return results if results else []
