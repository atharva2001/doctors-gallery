from langchain.agents import tool
from typing import TypedDict
import requests
import json

@tool
def get_all_appointments(page: int=1, per_page: int=10) -> str:
    """A tool that fetches all the appointment data.
    Args:
        page (int): The page number to fetch.
        per_page (int): The number of appointments per page."""
    response = requests.get(
        url=f"http://appointment_service:8003/appointments/get_all_appointments?page={page}&per_page={per_page}"
    )
    # print(response.content)
    return str(response.content)

@tool
def get_all_slots() -> str:
    """A tool that fetches all the slots data."""
    response = requests.get(
        url=f"http://appointment_service:8003/appointments/get_all_slots"
    )
    return str(response.content)

get_toolkit = [get_all_appointments, get_all_slots]



class AppointmentData(TypedDict):
    """A TypedDict for appointment data."""
    appointment_id: str
    patient_id: str
    doctor_id: str
    slot_id: str
    success: bool
    remarks: str

@tool
def create_appointment(data: AppointmentData) -> str:
    """A tool that create an appointment.
        {
            "appointment_id",
            "patient_id",
            "doctor_id",
            "slot_id",
            "success",
            "remarks"
        }   
    """
    try:
        response = requests.post(
            url="http://appointment_service:8003/appointments/create_appointment",
            json=data
        )
        return f"Success + {response.content}"
    except Exception as e:
        return f"Error: {str(e)}"
    

class SlotData(TypedDict):
    """TypedDict for slot data."""
    slot_id: int
    doctor_id: int
    date: str  # Format: "YYYY-MM-DD"
    time: str  # Format: "HH:MM:SS.sssZ"

@tool
def create_slot(data: SlotData) -> str:
    """A tool that create an slot.
        {
            "slot_id",
            "doctor_id",
            "date", # Format: "YYYY-MM-DD"
            "time" # Format: "HH:MM:SS.sssZ"
        }   
    """
    try:
        response = requests.post(
            url="http://appointment_service:8003/appointments/create_slot",
            json=data
        )
        return f"Success + {response.content}"
    except Exception as e:
        return f"Error: {str(e)}"

creation_toolkit = [create_appointment, create_slot]