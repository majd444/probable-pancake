import os
from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
from supabase import create_client, Client
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Enable debug logging for httpx
logging.getLogger('httpx').setLevel(logging.DEBUG)
logging.getLogger('httpcore').setLevel(logging.DEBUG)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

print(f"Loading Supabase client with URL: {supabase_url}")
print(f"Supabase key: {supabase_key[:10]}...")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase URL or key in environment variables")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    # Test the connection
    test = supabase.table('chatbots').select('*').limit(1).execute()
    print("Successfully connected to Supabase")
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")
    raise

async def verify_api_key(api_key: str, assistant_id: str) -> bool:
    """Verify if the provided API key is valid for the given assistant."""
    try:
        response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", assistant_id) \
            .eq("api_key", api_key) \
            .execute()
        
        if not response.data:
            logger.warning(f"Invalid API key or assistant ID. Assistant ID: {assistant_id}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error verifying API key: {str(e)}")
        return False

async def get_chatbot_id_from_session(session_id: str) -> str:
    """Get the chatbot ID associated with a session."""
    try:
        response = supabase.table("sessions") \
            .select("chatbot_id") \
            .eq("session_id", session_id) \
            .execute()
        
        if not response.data:
            logger.warning(f"No session found with ID: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        return response.data[0]["chatbot_id"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chatbot ID from session: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving session information")

async def get_chatbot_model(chatbot_id: str) -> str:
    """Get the model name for a chatbot."""
    try:
        response = supabase.table("chatbots") \
            .select("model_name") \
            .eq("id", chatbot_id) \
            .execute()
        
        if not response.data:
            logger.warning(f"No chatbot found with ID: {chatbot_id}")
            raise HTTPException(status_code=404, detail="Chatbot not found")
        
        return response.data[0]["model_name"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chatbot model: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving chatbot information")

app = FastAPI(
    title="SaaS AI Chatbot API",
    description="API for managing AI chatbot sessions and conversations",
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
print(f"OpenRouter API key: {OPENROUTER_API_KEY[:10]}..." if OPENROUTER_API_KEY else "OpenRouter API key not set")

# Debug logging for environment variables
logger.info(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
logger.info(f"Supabase key: {os.getenv('SUPABASE_KEY')}")
logger.info(f"OpenRouter key: {'*' * (len(OPENROUTER_API_KEY) - 4) + OPENROUTER_API_KEY[-4:] if OPENROUTER_API_KEY else 'Not set'}")

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

class ChatResponse(BaseModel):
    response: str

# Health check
@app.get("/health", response_model=str)
async def health_check():
    return "OK"

# Create a chat session (API)
@app.post("/api/chat/session", response_model=str, status_code=201)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    try:
        print(f"Attempting to create session for assistant_id: {request.assistant_id}")
        print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
        
        # Test Supabase connection
        try:
            test_response = supabase.table('chatbots').select('*').limit(1).execute()
            print(f"Supabase connection test: {test_response}")
        except Exception as e:
            print(f"Supabase connection error: {str(e)}")
            raise
            
        # Check if chatbot exists with the given API key
        response = supabase.table("chatbots") \
            .select("id") \
            .eq("id", request.assistant_id) \
            .eq("api_key", request.api_key) \
            .execute()
            
        print(f"Chatbot query response: {response}")
        
        if not response.data:
            raise HTTPException(
                status_code=403, 
                detail=f"Invalid API key or assistant ID. No matching chatbot found with id: {request.assistant_id}"
            )
        
        # Create a new session
        session_data = {
            "session_id": str(uuid.uuid4()),
            "chatbot_id": request.assistant_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        print(f"Creating session with data: {session_data}")
        session_response = supabase.table("sessions").insert(session_data).execute()
        print(f"Session creation response: {session_response}")
        
        if not session_response.data:
            raise HTTPException(status_code=500, detail="Failed to create session")
            
        return session_data["session_id"]
        
    except HTTPException as he:
        print(f"HTTPException in create_session: {he.detail}")
        raise
    except Exception as e:
        error_msg = f"Error creating session: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/chat", response_model=str, responses={
    200: {"description": "Successful Response"},
    400: {"model": ErrorResponse, "description": "Bad Request"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    403: {"model": ErrorResponse, "description": "Forbidden"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"}
})
async def chat(request: ChatRequest):
    """
    Process a chat message and return the assistant's response.
    
    - **api_key**: API key for authentication
    - **session_id**: ID of the chat session
    - **type**: Type of chat request
    - **assistant_id**: ID of the assistant
    - **messages**: List of messages in the conversation
    """
    try:
        # Validate api_key and assistant_id
        is_valid = await verify_api_key(request.api_key, request.assistant_id)
        if not is_valid:
            raise HTTPException(status_code=403, detail="Invalid API key or assistant ID")
            
        # Validate session
        chatbot_id = await get_chatbot_id_from_session(request.session_id)
        if not chatbot_id or chatbot_id != request.assistant_id:
            raise HTTPException(status_code=404, detail="Session not found or does not belong to the assistant")
            
        # Get the chatbot model
        model_name = await get_chatbot_model(request.assistant_id)
        if not model_name:
            raise HTTPException(status_code=500, detail="Chatbot configuration error")
            
        # Get conversation history
        prev_messages = supabase.table("conversations")\
            .select("role", "content")\
            .eq("session_id", request.session_id)\
            .order("timestamp")\
            .execute().data
            
        # Prepare messages for the LLM
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in prev_messages
        ]
        
        # Add new user messages
        for msg in request.messages:
            if msg.role == "user":
                messages.append({"role": msg.role, "content": msg.content})
                
        # Call OpenRouter API
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://pros.tools",
                "X-Title": "AI Chatbot SaaS"
            }
            
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            logger.info(f"Sending request to OpenRouter with model: {model_name}")
            logger.debug(f"Request headers: {headers}")
            logger.debug(f"Request payload: {payload}")
            
            openrouter_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.debug(f"OpenRouter response status: {openrouter_response.status_code}")
            logger.debug(f"OpenRouter response headers: {dict(openrouter_response.headers)}")
            logger.debug(f"OpenRouter response body: {openrouter_response.text}")
            
            openrouter_response.raise_for_status()
            ai_response = openrouter_response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_detail += f"\nResponse status: {e.response.status_code}"
                error_detail += f"\nResponse body: {e.response.text}"
            logger.error(f"OpenRouter API error: {error_detail}")
            raise HTTPException(status_code=500, detail=f"Error communicating with AI service: {error_detail}")
            
        # Save user messages to database
        for msg in request.messages:
            if msg.role == "user":
                supabase.table("conversations").insert({
                    "session_id": request.session_id,
                    "role": "user",
                    "content": msg.content,
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
                
        # Save AI response to database
        supabase.table("conversations").insert({
            "session_id": request.session_id,
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        
        # Update session last activity
        supabase.table("sessions")\
            .update({"last_activity": datetime.utcnow().isoformat()})\
            .eq("session_id", request.session_id)\
            .execute()
        
        return ai_response
        
    except HTTPException as he:
        logger.error(f"HTTP error in chat endpoint: {str(he.detail)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Widget endpoints
@app.post("/api/chat/widget/session", response_model=str)
async def create_widget_session(request: CreateWidgetSessionRequest):
    """
    Create a new chat session for the widget.
    
    - **chatbot_id**: ID of the chatbot to create a session for
    """
    try:
        # Verify chatbot exists
        response = supabase.table("chatbots").select("id").eq("id", request.chatbot_id).execute()
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Chatbot not found")
            
        # Generate a new session ID
        session_id = str(uuid.uuid4())
        
        # Store the session in the database
        supabase.table("sessions").insert({
            "session_id": session_id,
            "chatbot_id": request.chatbot_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "is_active": True,
            "is_widget": True
        }).execute()
        
        logger.info(f"Created new widget session: {session_id} for chatbot: {request.chatbot_id}")
        return ChatResponse(response="Widget session created successfully", session_id=session_id)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating widget session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/chat/widget", response_model=str)
async def widget_chat(request: WidgetChatRequest):
    """
    Process a chat message from the widget and return the assistant's response.
    
    - **session_id**: ID of the chat session
    - **message**: User's message content
    """
    try:
        # Get chatbot ID from session
        chatbot_id = await get_chatbot_id_from_session(request.session_id)
        if not chatbot_id:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Get the chatbot model
        model_name = await get_chatbot_model(chatbot_id)
        if not model_name:
            raise HTTPException(status_code=500, detail="Chatbot configuration error")
            
        # Get conversation history
        prev_messages = supabase.table("conversations")\
            .select("role", "content")\
            .eq("session_id", request.session_id)\
            .order("timestamp")\
            .execute().data
            
        # Prepare messages for the LLM
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in prev_messages
        ]
        
        # Add the new user message
        messages.append({"role": "user", "content": request.message})
        
        # Call OpenRouter API
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://pros.tools",
                "X-Title": "AI Chatbot Widget"
            }
            
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            logger.info(f"Sending request to OpenRouter with model: {model_name}")
            logger.debug(f"Request headers: {headers}")
            logger.debug(f"Request payload: {payload}")
            
            openrouter_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.debug(f"OpenRouter response status: {openrouter_response.status_code}")
            logger.debug(f"OpenRouter response headers: {dict(openrouter_response.headers)}")
            logger.debug(f"OpenRouter response body: {openrouter_response.text}")
            
            openrouter_response.raise_for_status()
            ai_response = openrouter_response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_detail += f"\nResponse status: {e.response.status_code}"
                error_detail += f"\nResponse body: {e.response.text}"
            logger.error(f"OpenRouter API error: {error_detail}")
            raise HTTPException(status_code=500, detail=f"Error communicating with AI service: {error_detail}")
        
        # Save user message to database
        supabase.table("conversations").insert({
            "session_id": request.session_id,
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        
        # Save AI response to database
        supabase.table("conversations").insert({
            "session_id": request.session_id,
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }).execute()
        
        # Update session last activity
        supabase.table("sessions")\
            .update({"last_activity": datetime.utcnow().isoformat()})\
            .eq("session_id", request.session_id)\
            .execute()
        
        return ai_response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in widget chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Add this at the end of the file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)