from fastapi import APIRouter, Depends, HTTPException, Request, Header
from ..database import login
from ..model.User import User
from ..model.Login import Login
from ..common_utils.password_hash import verify_password
from starlette import status
from ..common_utils import jwt_utils
import json
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/login",
    tags=["Login"],
)

@router.get("/", status_code=status.HTTP_200_OK)
async def user_login(data: Login, request: Request):
    email = data.email
    password = data.password
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    cursor = request.app.state.client.cursor()
    response = await login.get_user_by_email(cursor, email)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    print(email, password)
    user = response[0]

    if not verify_password(password, response[-2]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    jwt_token = jwt_utils.create_access_token(data={"sub": email, "role": response[-1]})
    return {"message": "Login successful", "user_id": user, "access_token": jwt_token, "token_type": "bearer", "role": response[-1]}


@router.get("/logout", status_code=status.HTTP_200_OK)
async def user_logout(request: Request, authorization: str = Header(None)):
    if not authorization:
        return HTTPException(status_code=401, detail="Authorization header missing")
    
    data = jwt_utils.decode_token(authorization.split(" ")[1])
    if not data or "sub" not in data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    jwt_token = jwt_utils.create_access_token(data={"sub": data["sub"]}, expires_delta=timedelta(minutes=0))
    return {
        "message": "Logout Successful",
    }


@router.get("/get_user/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: str, request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer ") or not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    res = (jwt_utils.decode_token(auth_header.split(" ")[1]) if auth_header else None)
    
    if not res or "sub" not in res:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    cache = request.app.state.redis_client.get(f"login/get_user/{id}")
    if cache:
        return json.loads(cache)
    else:

        cursor = request.app.state.client.cursor()
        response = await login.get_user_by_id(cursor, id)
        
        if "error" in response:
            raise HTTPException(status_code=404, detail=response["error"])
        
        request.app.state.redis_client.set(f"login/get_user/{id}", json.dumps(response))

        return response


@router.get("/get_all_users", status_code=status.HTTP_200_OK)
async def get_all_users(request: Request):
    cache = request.app.state.redis_client.get("login/get_all_users")
    if cache:
        return {"users": cache}
    else:
        cursor = request.app.state.client.cursor()
        response = await login.get_all_users(cursor)
        request.app.state.redis_client.set("login/get_all_users", json.dumps(response))
    
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response


@router.delete("/delete_user/{id}", status_code=status.HTTP_200_OK)
async def delete_user(id: str, request: Request):
    cursor = request.app.state.client.cursor()
    if await get_user(id, request):

        response = await login.delete_user(cursor, id)
        if "error" in response:
            raise HTTPException(status_code=404, detail=response["error"])
        
        request.app.state.redis_client.delete("login/get_all_users")
        request.app.state.redis_client.delete(f"login/get_user/{id}")
        return response
    return {"message": "User not found."}