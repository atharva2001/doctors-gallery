import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import redis
import os

from app.database.core import get_db, engine, Base
from app.routes.appointment import router as appointment_router


limiter = Limiter(key_func=get_remote_address, default_limits=["2/second"])
REDIS_HOST = os.getenv("REDIS_HOST", "0.0.0.0")
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.client = get_db()
        app.state.redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        
        yield 
        app.state.client.close()

    except Exception as e:
        print(f"Error during lifespan: {e}")
        raise e

app = FastAPI(
    title="Appointment Service",
    version="1.0.0",
    description="Service for managing appointments",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity; adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)

app.include_router(appointment_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Appointment Service"}


if __name__ =="__main__":
    uvicorn.run("main:app", 
                host="0.0.0.0", 
                port=8003, 
                reload=True)