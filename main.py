from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Pydantic models
class CreateSessionRequest(BaseModel):
    api_key: str
    assistant_id: str

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    api_key: str
    session_id: str
    type: str
    assistant_id: str
    messages: List[Message]

class CreateWidgetSessionRequest(BaseModel):
    chatbot_id: str

class WidgetChatRequest(BaseModel):
    session_id: str
    message: str

# API endpoints
@app.post("/api/chat/session")
async def create_session(request: CreateSessionRequest):
    response = supabase.table("chatbots").select("id").eq("id", request.assistant_id).eq("api_key", request.api_key).execute()
    if not response.data:
        raise HTTPException(status_code=403, detail="Invalid API key or assistant ID")
    session_id = str(uuid.uuid4())
    supabase.table("sessions").insert({
        "session_id": session_id,
        "chatbot_id": request.assistant_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return {"session_id": session_id}

# ... (rest of the endpoints from your guide)