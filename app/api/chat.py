from fastapi import APIRouter, Body, HTTPException
import sqlite3
import datetime
from pathlib import Path
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.llm.main_llm import MainLLM
from typing import List, Dict

# Create router
chat_router = APIRouter(prefix="/api", tags=["chat"])

# Create database path
DB_DIR = Path("./data")
DB_FILE = DB_DIR / "myai.db"

# Ensure DB directory exists
DB_DIR.mkdir(exist_ok=True)

main_llm = None

def load_chat_history():
    """Load chat history from SQLite database - last 20 messages"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, parts FROM chat ORDER BY id DESC LIMIT 20")
        print("Loaded chat history from database")
        return [{"role": row[0], "parts": row[1]} for row in reversed(cursor.fetchall())]
    
def save_chat_message(role: str, message: str):
    """Save chat message to SQLite database"""
    timestamp = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat (timestamp, role, parts) VALUES (?, ?, ?)",
            (timestamp, role, message)
        )
        conn.commit()
    print("Saved message to database:", message)
    
@chat_router.post("/chat", response_model=ChatResponse)
async def create_chat(request: ChatRequest = Body(...)):
    """Process chat request and generate response"""
    try:
        global main_llm
        
        # Initialize MainLLM only once with chat history (singleton pattern)
        if main_llm is None:
            history = load_chat_history()
            main_llm = MainLLM(history=history)
        
        # Use MainLLM for all responses (it already handles web search internally)
        response_text = main_llm.process_chat(
            request.message, 
            with_search=request.web_search_enabled
        )
        
        # Save both user message and AI response to storage
        save_chat_message("user", request.message)
        save_chat_message("model", response_text)
        
        # Determine if web search was used (this is just for the response model)
        # We can assume web search was used if web_search_enabled is True
        used_web_search = request.web_search_enabled
        
        return ChatResponse(response=response_text, used_web_search=used_web_search)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@chat_router.get("/chat/history")
async def get_chat_history():
    """Get chat history from database for display in UI"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, role, parts FROM chat ORDER BY id")
            rows = cursor.fetchall()
            
            # Format the chat history as a list of messages
            messages = []
            for row in rows:
                messages.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "role": row[2],
                    "content": row[3]
                })
            
            return {"messages": messages}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")