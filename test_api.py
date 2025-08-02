import os
import sys
import pytest
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_API_KEY = os.getenv("TEST_API_KEY", "c8bc40f2-e83d-4e92-ac2b-d5bd6444da0a")
TEST_ASSISTANT_ID = os.getenv("TEST_ASSISTANT_ID", "e97f4988-4f70-470b-b2e5-aca28ddbcff0")

def test_health_check():
    """Test the health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✅ Health check passed")

def test_create_session():
    """Test creating a new chat session."""
    data = {
        "api_key": TEST_API_KEY,
        "assistant_id": TEST_ASSISTANT_ID
    }
    response = requests.post(f"{BASE_URL}/api/chat/session", json=data)
    assert response.status_code == 200
    assert "session_id" in response.json()
    session_id = response.json()["session_id"]
    print(f"✅ Session created with ID: {session_id}")
    return session_id

def test_chat(session_id):
    """Test sending a chat message."""
    data = {
        "api_key": TEST_API_KEY,
        "session_id": session_id,
        "type": "message",
        "assistant_id": TEST_ASSISTANT_ID,
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=data)
    assert response.status_code == 200
    assert "response" in response.json()
    print(f"✅ Chat response: {response.json()['response'][:50]}...")

def test_widget_session():
    """Test creating a widget session."""
    data = {
        "chatbot_id": TEST_ASSISTANT_ID
    }
    response = requests.post(f"{BASE_URL}/api/chat/widget/session", json=data)
    assert response.status_code == 200
    assert "session_id" in response.json()
    session_id = response.json()["session_id"]
    print(f"✅ Widget session created with ID: {session_id}")
    return session_id

def test_widget_chat(session_id):
    """Test sending a widget chat message."""
    data = {
        "session_id": session_id,
        "message": "Hello from widget!"
    }
    response = requests.post(f"{BASE_URL}/api/chat/widget", json=data)
    assert response.status_code == 200
    assert "response" in response.json()
    print(f"✅ Widget chat response: {response.json()['response'][:50]}...")

if __name__ == "__main__":
    # Run tests
    print("🚀 Starting API tests...")
    
    # Test health check
    test_health_check()
    
    # Test regular chat flow
    print("\n🔍 Testing regular chat flow...")
    session_id = test_create_session()
    test_chat(session_id)
    
    # Test widget flow
    print("\n🔍 Testing widget flow...")
    widget_session_id = test_widget_session()
    test_widget_chat(widget_session_id)
    
    print("\n✨ All tests completed successfully!")
    sys.exit(0)
