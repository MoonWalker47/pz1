import os
import time
from fastapi import FastAPI
import psycopg2

app = FastAPI(title="Task API")

# DB connection config
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "password")

def get_db_connection():
    # Retry loop for DB availability on startup
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
            )
            return conn
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("Failed to connect to DB")

@app.on_event("startup")
def startup_db():
    # Create target table if not exists
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "FastAPI Ops"}

@app.get("/api/logs")
def get_logs():
    # Fetch all logs from DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, ts, message FROM logs ORDER BY ts DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "timestamp": r[1], "message": r[2]} for r in rows]

@app.post("/api/logs")
def create_log(message: str):
    # Insert new log entry
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (message) VALUES (%s) RETURNING id;", (message,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "created"}
