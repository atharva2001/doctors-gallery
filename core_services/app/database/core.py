import os
from dotenv import load_dotenv
import motor.motor_asyncio
import asyncio


MONGO_URI = os.getenv("MONGO_CLIENT_URI", "0.0.0.0")
USER = os.getenv("MONGO_USER", "admin")
PASSWORD = os.getenv("MONGO_PASSWORD", "secret")
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://admin:secret@0.0.0.0:27017")

print(MONGO_URI)
def get_db_connection():
    try:

        client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
        # Access your database and collection
        return client
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise e
