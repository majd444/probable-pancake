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

app = FastAPI(
    title="SaaS AI Chatbot API",
    description="API for the SaaS AI Chatbot service",
    version="1.0.0",
    openapi_url="/openapi.json"
)

# Enable CORS for widget access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific domains in production
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

# Schemas
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

class ErrorResponse(BaseModel):
    detail: str

class ValidationError(BaseModel):
    loc: List[str]
    msg: str
    type: str

class HTTPValidationError(BaseModel):
    detail: List[ValidationError]

# Health check
@app.get("/health", response_model=str)
async def health_check():
    return "OK"

# Create a chat session (API)
@app.post("/api/chat/session", response_model=str, status_code=201)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    response = supabase.table("chatbots").select("id").eq("id", request.assistant_id).eq("api_key", request.api_key).execute()
    if not response.data:
        raise HTTPException(status_code=403, detail="Invalid API key or assistant ID")
    session_id = str(uuid.uuid4())
    supabase.table("sessions").insert({
        "session_id": session_id,
        "chatbot_id": request.assistant_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return session_id

# Send a message (API)
@app.post("/api/chat", response_model=str)
async def chat(request: ChatRequest):
    """Process a chat message"""
    response = supabase.table("chatbots").select("model_name").eq("id", request.assistant_id).eq("api_key", request.api_key).execute()
    if not response.data:
        raise HTTPException(status_code=403, detail="Invalid API key or assistant ID")
    model_name = response.data[0]["model_name"]
    session_response = supabase.table("sessions").select("session_id").eq("session_id", request.session_id).eq("chatbot_id", request.assistant_id).execute()
    if not session_response.data:
        raise HTTPException(status_code=404, detail="Session not found or does not belong to the assistant")
    prev_messages = supabase.table("conversations").select("role", "content").eq("session_id", request.session_id).order("timestamp").execute().data
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in prev_messages]
    messages.extend([{"role": msg.role, "content": msg.content} for msg in request.messages if msg.role == "user"])
    try:
        openrouter_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://pros.tools",
                "X-Title": "AI Chatbot SaaS"
            },
            json={
                "model": model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        openrouter_response.raise_for_status()
        ai_response = openrouter_response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with AI: {str(e)}")
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
    return ai_response

# Create a session for widget
@app.post("/api/chat/widget/session", response_model=str)
async def create_widget_session(request: CreateWidgetSessionRequest):
    """Create a new session for the widget"""
    response = supabase.table("chatbots").select("id").eq("id", request.chatbot_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    session_id = str(uuid.uuid4())
    supabase.table("sessions").insert({
        "session_id": session_id,
        "chatbot_id": request.chatbot_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return session_id

# Send a message for widget
@app.post("/api/chat/widget", response_model=str)
async def widget_chat(request: WidgetChatRequest):
    """Process a widget chat message"""
    session_response = supabase.table("sessions").select("chatbot_id").eq("session_id", request.session_id).execute()
    if not session_response.data:
        raise HTTPException(status_code=404, detail="Session not found")
    chatbot_id = session_response.data[0]["chatbot_id"]
    chatbot_response = supabase.table("chatbots").select("model_name").eq("id", chatbot_id).execute()
    if not chatbot_response.data:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    model_name = chatbot_response.data[0]["model_name"]
    prev_messages = supabase.table("conversations").select("role", "content").eq("session_id", request.session_id).order("timestamp").execute().data
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in prev_messages]
    messages.append({"role": "user", "content": request.message})
    try:
        openrouter_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://pros.tools",
                "X-Title": "AI Chatbot SaaS"
            },
            json={
                "model": model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )
        openrouter_response.raise_for_status()
        ai_response = openrouter_response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with AI: {str(e)}")
    supabase.table("conversations").insert([
        {"session_id": request.session_id, "role": "user", "content": request.message, "timestamp": datetime.utcnow().isoformat()},
        {"session_id": request.session_id, "role": "assistant", "content": ai_response, "timestamp": datetime.utcnow().isoformat()}
    ]).execute()
    return ai_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
