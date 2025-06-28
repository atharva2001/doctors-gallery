from fastapi import APIRouter, HTTPException, Request, Header
from starlette import status
import requests
import json
from app.database import doctors

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"],
)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_doctor_info(request: Request, authorization: str = Header(None)):
    # print("here")
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
    if response.json()["role"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not authorized to access this resource."
        )
    
    cache = request.app.state.redis_client.get(f"doctors/me/{id}")
    if cache:
        return json.loads(cache)
    else:
        response = requests.get(
            url=f"http://auth_service:8000/login/get_user/{id}",
            headers={"Authorization": f"Bearer {authorization}"}
        )
        data = response.json()
        print(data)
        user_data = {}
        user_data["id"] = data[0]
        user_data["name"] = data[1]
        user_data["email"] = data[2]

        db = request.app.state.client["doctors"]
        doctors_collection = "doctors_collection"
        res = await doctors.insert_data(db, doctors_collection, user_data)
        print(res)
        request.app.state.redis_client.set(f"doctors/me/{id}", json.dumps(user_data))
        return response.json()

@router.put("/me/update", status_code=status.HTTP_200_OK)
async def update_doctor_info(request: Request, authorization: str = Header(None), user_data: dict = None):
    try:
        response = requests.get(
            "http://auth_service:8000/verify-token",  
            headers={"Authorization": f"Bearer {authorization}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        if response.json()["role"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You are not authorized to access this resource."
            )
        # Logic
        db = request.app.state.client["doctors"]
        doctors_collection = "doctors_collection"
        res = await doctors.update_data(db, doctors_collection, user_data)
        print(res)
        request.app.state.redis_client.delete(f"doctors/me/{user_data['id']}")
        
        return {"message": "Doctors information updated successfully"}

        
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to the authentication service: {str(e)}"
        )

