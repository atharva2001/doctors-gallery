from fastapi import APIRouter, HTTPException, Request, Header
from starlette import status
import requests
import json
from app.database import patients

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_patient_info(request: Request, authorization: str = Header(None)):
    id = request.headers.get("id") 
    response = requests.get(
        url=f"http://auth_service:8000/verify-token",
        headers={"Authorization": f"Bearer {authorization}"}
    )
    if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
    # print(response.json())
    if response.json()["role"] != "users":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not authorized to access this resource."
        )
    
    cache = request.app.state.redis_client.get(f"patients/me/{id}")
    if cache:
        return json.loads(cache)
    else:
        response = requests.get(
            url=f"http://auth_service:8000/login/get_user/{id}",
            headers={"Authorization": f"Bearer {authorization}"}
        )
        data = response.json()
        # print(data)
        user_data = {}
        user_data["id"] = data[0]
        user_data["name"] = data[1]
        user_data["email"] = data[2]

        db = request.app.state.client["patients"]
        patient_collection = "patients_collection"
        res = await patients.insert_data(db, patient_collection, user_data)
        print(res)
        request.app.state.redis_client.set(f"patients/me/{id}", json.dumps(user_data))

        return response.json()

@router.put("/me/update", status_code=status.HTTP_200_OK)
async def update_patient_info(request: Request, authorization: str = Header(None), user_data: dict = None):
    try:
        response = requests.get(
        url=f"http://auth_service:8000/verify-token",
        headers={"Authorization": f"Bearer {authorization}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        if response.json()["role"] != "users":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to access this resource."
            )
        
        # Logic
        db = request.app.state.client["patients"]
        patient_collection = "patients_collection"
        res = await patients.update_data(db, patient_collection, user_data)
        print(res)
        request.app.state.redis_client.delete(f"patients/me/{user_data['id']}")
        return {"message": "Patient information updated successfully"}

        
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to the authentication service: {str(e)}"
        )

