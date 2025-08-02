from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SaaS AI Chatbot API",
    description="API for the SaaS AI Chatbot service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    api_key: str
    session_id: str
    type: str
    assistant_id: str
    messages: List[Message]

class CreateSessionRequest(BaseModel):
    api_key: str
    assistant_id: str

class CreateWidgetSessionRequest(BaseModel):
    chatbot_id: str

class WidgetChatRequest(BaseModel):
    session_id: str
    message: str

# Dependency to verify API key
async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    return api_key

# API Endpoints
@app.post("/api/chat/session", status_code=status.HTTP_201_CREATED)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    # Verify the API key and assistant ID
    response = supabase.table("chatbots") \
        .select("id") \
        .eq("id", request.assistant_id) \
        .eq("api_key", request.api_key) \
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key or assistant ID"
        )
    
    # Create a new session
    session_id = str(uuid.uuid4())
    supabase.table("sessions").insert({
        "session_id": session_id,
        "chatbot_id": request.assistant_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    return {"session_id": session_id}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Process a chat message"""
    # Verify the API key and assistant ID
    response = supabase.table("chatbots") \
        .select("model_name") \
        .eq("id", request.assistant_id) \
        .eq("api_key", request.api_key) \
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key or assistant ID"
        )
    
    model_name = response.data[0]["model_name"]
    
    # Verify the session
    session_response = supabase.table("sessions") \
        .select("session_id") \
        .eq("session_id", request.session_id) \
        .eq("chatbot_id", request.assistant_id) \
        .execute()
    
    if not session_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or does not belong to the assistant"
        )
    
    # Get conversation history
    prev_messages = supabase.table("conversations") \
        .select("role", "content") \
        .eq("session_id", request.session_id) \
        .order("timestamp") \
        .execute().data
    
    # Prepare messages for the AI
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in prev_messages]
    
    # Add new user messages
    for msg in request.messages:
        if msg.role == "user":
            messages.append({"role": msg.role, "content": msg.content})
    
    # Call OpenRouter (or your AI service)
    try:
        # This is a placeholder - you'll need to implement the actual AI call
        ai_response = "This is a placeholder response. Implement the AI call here."
        
        # Save user messages and AI response to the database
        for msg in request.messages:
            if msg.role == "user":
                supabase.table("conversations").insert({
                    "session_id": request.session_id,
                    "role": "user",
                    "content": msg.content,
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
        
        supabase.table("conversations").insert({
            "session_id": request.session_id,
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        
        return {"response": ai_response}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing your request: {str(e)}"
        )

# Widget endpoints
@app.post("/api/chat/widget/session")
async def create_widget_session(request: CreateWidgetSessionRequest):
    """Create a new session for the widget"""
    response = supabase.table("chatbots") \
        .select("id") \
        .eq("id", request.chatbot_id) \
        .execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    session_id = str(uuid.uuid4())
    supabase.table("sessions").insert({
        "session_id": session_id,
        "chatbot_id": request.chatbot_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    return {"session_id": session_id}

@app.post("/api/chat/widget")
async def widget_chat(request: WidgetChatRequest):
    """Process a widget chat message"""
    # Verify the session
    session_response = supabase.table("sessions") \
        .select("chatbot_id") \
        .eq("session_id", request.session_id) \
        .execute()
    
    if not session_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    chatbot_id = session_response.data[0]["chatbot_id"]
    
    # Get the chatbot model
    chatbot_response = supabase.table("chatbots") \
        .select("model_name") \
        .eq("id", chatbot_id) \
        .execute()
    
    if not chatbot_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    model_name = chatbot_response.data[0]["model_name"]
    
    # Get conversation history
    prev_messages = supabase.table("conversations") \
        .select("role", "content") \
        .eq("session_id", request.session_id) \
        .order("timestamp") \
        .execute().data
    
    # Prepare messages for the AI
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in prev_messages]
    messages.append({"role": "user", "content": request.message})
    
    try:
        # This is a placeholder - implement the actual AI call
        ai_response = f"This is a response to: {request.message}"
        
        # Save messages to the database
        supabase.table("conversations").insert([
            {
                "session_id": request.session_id,
                "role": "user",
                "content": request.message,
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "session_id": request.session_id,
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]).execute()
        
        return {"response": ai_response}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing your message: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
