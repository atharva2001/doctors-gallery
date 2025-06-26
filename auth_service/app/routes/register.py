from fastapi import APIRouter, Request, HTTPException, Depends
from ..database import register
from ..model.User import User
from passlib.context import CryptContext
from ..common_utils.password_hash import hash_pass
from starlette import status
from ..common_utils import jwt_utils

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
    
    jwt_token = jwt_utils.create_access_token(data={"sub": user.email})
    request.app.state.redis_client.delete(f"get_users")
    request.app.state.redis_client.delete(f"get_all_users")
    return {
        "message": "User created successfully",
        "user_id": user.email,
        "access_token": jwt_token,
        "token_type": "bearer",
    }