from fastapi import APIRouter, Request, HTTPException, Depends
from ..database import register
from ..model.User import User
from ..model.Message import Message
from passlib.context import CryptContext
from ..common_utils.password_hash import hash_pass
from starlette import status
from ..common_utils import jwt_utils
import requests

router = APIRouter(
    prefix="/register",
    tags=["Register"],
)


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(user: User, request: Request):
    cursor = request.app.state.client.cursor()
    # user.password = hash_pass(user.password)
    response = await register.create_user(cursor, user)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    
    if user.role == "doctor":
        try:
            message = Message(key="new_doctor", content=f"New doctor registered: {user.email}")
            response = requests.post("http://notification_service:8005/create-topic?topic_name=new_doc_notifier")
        except Exception as e:
            pass 
        finally:
            response = requests.post(f"http://notification_service:8005/create_message?topic=new_doc_notifier&message={str(message)}")

    jwt_token = jwt_utils.create_access_token(data={"sub": user.email})
    request.app.state.redis_client.delete("login/get_all_users")
    return {
        "message": "User created successfully",
        "user_email": user.email,
        "access_token": jwt_token,
        "token_type": "bearer",
        "role": user.role
    }
