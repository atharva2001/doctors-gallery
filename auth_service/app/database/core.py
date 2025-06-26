import psycopg2
import os
from dotenv import load_dotenv

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "0.0.0.0")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="auth_service",
            user="postgres",
            password="postgres",
            host=POSTGRES_HOST,
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise e
