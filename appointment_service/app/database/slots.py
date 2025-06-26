from app.database.core import Base 
from sqlalchemy import TIMESTAMP, Column, String, Boolean, Integer, Date, Time
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE


class Slot(Base):
    __tablename__ = "slots"
    
    slot_id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)


def get_all_slots(db):
    results = db.query(Slot).all()
    return results if results else []

def get_slot_by_doctor_id(db, doctor_id: int):
    results = db.query(Slot).filter(Slot.doctor_id == doctor_id).all()
    return results if results else []