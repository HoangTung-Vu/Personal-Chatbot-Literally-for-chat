import os
import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Import routers
from app.api.chat import chat_router

# Load environment variables
load_dotenv()

# Create app
app = FastAPI(title="Personal AI Assistant")

# Initialize database
DB_DIR = Path("./data")
DB_FILE = DB_DIR / "myai.db"
DB_DIR.mkdir(exist_ok=True)

def init_db():
    """Initialize SQLite database with required tables"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            parts TEXT NOT NULL
        )
        ''')
        conn.commit()
    print("Database initialized")

# Initialize database
init_db()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(chat_router)

# Root route to serve the frontend
@app.get("/")
async def read_root():
    return FileResponse("templates/index.html")

# Run with: uvicorn run:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
