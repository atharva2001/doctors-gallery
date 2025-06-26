from fastapi import FastAPI, Header, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware 
from contextlib import asynccontextmanager
from app.routes.login import router as login_router
from app.routes.register import router as register_router
from app.database.core import get_db_connection
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import redis
from app.common_utils.jwt_utils import decode_token
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
    title="Auth Service",
    description="Authentication service for the application",
    version="1.0.0",    
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)

app.include_router(login_router)
app.include_router(register_router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auth Service"}

@app.get("/verify-token", status_code=200)
async def verify_test(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    data = decode_token(authorization.split(" ")[1])
    print(data)
    if not data or "sub" not in data:
        raise HTTPException(status_code=401, detail="Invalid token")

    return data
    


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )