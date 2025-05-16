from pydantic import BaseModel

class ChatRequest(BaseModel):
    """Model for chat request from user"""
    message: str
    web_search_enabled: bool = True  # Toggle for web search feature

class ChatResponse(BaseModel):
    """Model for chat response to user"""
    response: str
    used_web_search: bool = False  # Indicates if web search was used