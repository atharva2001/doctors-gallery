from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query, Response
from app.model.appointment import Appointment as AppointmentSchema, AppointmentNotification
from app.model.slots import Slot as SlotSchema, SlotNotification
from starlette import status
from app.database import appointment, slots
from sqlalchemy.orm import Session
from app.database.core import get_db
from app.database.appointment import Appointment as AppointmentModel
from app.database.slots import Slot as SlotModel
import json
import requests

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)

def get_pagination_params(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1)
):
    return {"page": page, "per_page": per_page}

@router.get("/get_all_appointments", status_code=status.HTTP_200_OK)
async def get_all_appointments(request: Request, db: Session=Depends(get_db), authorization: str = Header(None), pagination: dict = Depends(get_pagination_params), response: Response = None):
    # Placeholder for fetching all appointments
    page = pagination["page"]
    per_page = pagination["per_page"]  
    cache = request.app.state.redis_client.get(f"appointment/all_appointments")
    start = (page - 1) * per_page
    end = start + per_page

    if cache:
        data = json.loads(cache)
        return data[start:end] if data else []
    else:
        
        

        result = appointment.get_all_appointments(db)
        appointment_list = []
        for res in result:
            appointment_list.append(
                {
                    "appointmen_id": res.appointment_id,
                    "patient_id": res.patient_id,
                    "doctor_id": res.doctor_id,
                    "slot_id": res.slot_id,
                    "success": res.success,
                    "remarks": res.remarks
                }            
            )

        response.headers["X-Total-Count"] = str(len(result))
        response.headers["X-Page"] = str(page)
        response.headers["X-Per-Page"] = str(per_page)
        request.app.state.redis_client.set(f"appointment/all_appointments", json.dumps(appointment_list))

        return result[start:end] if result else []


@router.post("/create_appointment", status_code=status.HTTP_201_CREATED)
async def create_appointment(appointment_data: AppointmentSchema, request: Request, db: Session = Depends(get_db)):
    # Placeholder for creating an appointment
    try:
        print(appointment_data)
        new_appointment = AppointmentModel(
            appointment_id=appointment_data.appointment_id,
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            slot_id=appointment_data.slot_id,
            success=appointment_data.success,
            remarks=appointment_data.remarks
        )
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        request.app.state.redis_client.delete(f"appointment/all_appointments") 
        app_notify = AppointmentNotification(
            key="new_appointment",
            content=f"New appointment created: {new_appointment.appointment_id} for patient {new_appointment.patient_id} with doctor {new_appointment.doctor_id} at slot {new_appointment.slot_id}"
        )
        response = requests.post(f"http://notification_service:8005/create_message?topic=new_doc_notifier&message={str(app_notify)}")
        return {"message": "Appointment created successfully", "appointment_id": new_appointment}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.get("/get_all_slots", status_code=status.HTTP_200_OK)
async def get_all_slots(request: Request, db: Session=Depends(get_db), authorization: str = Header(None), pagination: dict = Depends(get_pagination_params), response: Response = None):
    # Placeholder for fetching all appointments
    page = pagination["page"]
    per_page = pagination["per_page"]
    cache = request.app.state.redis_client.get(f"appointment/all_slots")
    start = (page - 1) * per_page
    end = start + per_page
    if cache:
        data = json.loads(cache)
        return data[start:end] if data else []
    else:
    
        result = slots.get_all_slots(db)
        response.headers["X-Total-Count"] = str(len(result))
        response.headers["X-Page"] = str(page)
        response.headers["X-Per-Page"] = str(per_page)
        slot_list = []
        for res in result:
            slot_list.append(
                {
                    "slot_id": res.slot_id,
                    "doctor_id": res.doctor_id,
                    "date": res.date.isoformat() if res.date else None,
                    "time": res.time.isoformat() if res.time else None
                }
            )
        request.app.state.redis_client.set(f"appointment/all_slots", json.dumps(slot_list))
        

        return slot_list[start:end] if result else []
    
@router.post("/create_slot", status_code=status.HTTP_201_CREATED)
async def create_slot(slot_data: SlotSchema, request: Request, db: Session = Depends(get_db)):
    try:
        print(slot_data)
        new_slot = SlotModel(
            slot_id=slot_data.slot_id,
            doctor_id=slot_data.doctor_id,
            date=slot_data.date,
            time=slot_data.time
        )
        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)
        request.app.state.redis_client.delete(f"appointment/all_slots") 
        slot_notify = SlotNotification(
            key="new_slot",
            content=f"New slot created: {new_slot.slot_id} for doctor {new_slot.doctor_id} on {new_slot.date} at {new_slot.time}"
        )
        response = requests.post(f"http://notification_service:8005/create_message?topic=new_doc_notifier&message={str(slot_notify)}")
        return {"message": "Slot created successfully", "slot_id": new_slot.slot_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
    

@router.get("/get_slots_by_doctor_id/{doctor_id}", status_code=status.HTTP_200_OK)
async def get_slots_by_doctor_id(doctor_id: int, request: Request, db: Session = Depends(get_db), authorization: str = Header(None)):
    try:
        cache = request.app.state.redis_client.get(f"appointment/slots_by_doctor/{doctor_id}")
        if cache:
            return json.loads(cache)
        else:
            slots_by_doctor = slots.get_slot_by_doctor_id(db, doctor_id)
            if not slots_by_doctor:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No slots found for this doctor")
            slot_list = []
            for slot in slots_by_doctor:
                slot_list.append(
                    {
                        "slot_id": slot.slot_id,
                        "doctor_id": slot.doctor_id,
                        "date": slot.date.isoformat() if slot.date else None,
                        "time": slot.time.isoformat() if slot.time else None
                    }
                )
            request.app.state.redis_client.set(f"appointment/slots_by_doctor/{doctor_id}", json.dumps(slot_list))
            return slots_by_doctor
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.get("/get_appointment_by_patient_id/{appointment_id}", status_code=status.HTTP_200_OK)
async def get_appointment_by_patient_id(appointment_id: int, request: Request, db: Session = Depends(get_db), authorization: str = Header(None)):
    try:
        cache = request.app.state.redis_client.get(f"appointment/appointment_by_patient/{appointment_id}")
        if cache:
            return json.loads(cache)
        else:
            appointment_data = appointment.get_appointment_by_patient_id(db, appointment_id)
            if not appointment_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
            appointment_list = []
            for app in appointment_data:
                appointment_list.append(
                    {
                        "appointment_id": app.appointment_id,
                        "patient_id": app.patient_id,
                        "doctor_id": app.doctor_id,
                        "slot_id": app.slot_id,
                        "success": app.success,
                        "remarks": app.remarks
                    }
                )
            request.app.state.redis_client.set(f"appointment/appointment_by_patient/{appointment_id}", json.dumps(appointment_list))
            return appointment_data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
