from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Header
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import requests
from app.database.core import get_db_connection
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.routes.patients import router as patients_router
from app.routes.doctors import router as doctors_router
import os

limiter = Limiter(key_func=get_remote_address, default_limits=["2/second"])
REDIS_HOST = os.getenv("REDIS_HOST", "0.0.0.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.client = get_db_connection()
        app.state.redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        yield
        app.state.client.close()
    except Exception as e:
        print(f"Error during lifespan: {e}")
        raise e

app = FastAPI(
    title="Core Services API",
    description="API for core services of the application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)   
app.include_router(patients_router)
app.include_router(doctors_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Core Services API"}

@app.get("/test", status_code=200)
async def test_endpoint(authorization: str = Header(None)):
    print(authorization, type(authorization))
    try:
        response = requests.get(
            "http://127.0.0.1:8000/verify-token",  
            headers={"Authorization": f"Bearer {authorization}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
    
    except HTTPException as e:
        # print(f"Error connecting to the authentication service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error connecting to the authentication service: {str(e)}"
        )
    return {"message": response.json()}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=8001,
        reload=True, 
        )