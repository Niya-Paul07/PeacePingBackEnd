import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    database="peaceping",
    user="postgres",
    password=os.getenv("DB_PASSWORD"),
    port="5432"
)

cur = conn.cursor()