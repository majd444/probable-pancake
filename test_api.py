import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "c8bc40f2-e83d-4e92-ac2b-d5bd6444da0a"  # From your test chatbot
ASSISTANT_ID = "e97f4988-4f70-470b-b2e5-aca28ddbcff0"  # From your test chatbot

def test_create_session():
    """Test creating a new chat session."""
    url = f"{BASE_URL}/api/chat/session"
    data = {
        "api_key": API_KEY,
        "assistant_id": ASSISTANT_ID
    }
    
    print("Creating a new session...")
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        session_id = response.json()["session_id"]
        print(f"✅ Session created successfully. Session ID: {session_id}")
        return session_id
    else:
        print(f"❌ Failed to create session. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_send_message(session_id):
    """Test sending a message to the chat."""
    if not session_id:
        print("❌ No session ID provided. Cannot send message.")
        return
        
    url = f"{BASE_URL}/api/chat"
    data = {
        "api_key": API_KEY,
        "session_id": session_id,
        "type": "custom_code",
        "assistant_id": ASSISTANT_ID,
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ]
    }
    
    print("\nSending a message...")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("✅ Message sent successfully.")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Failed to send message. Status: {response.status_code}")
        print(f"Response: {response.text}")

def test_widget_flow():
    """Test the widget flow (create session and send message)."""
    # Create a widget session
    url = f"{BASE_URL}/api/chat/widget/session"
    data = {
        "chatbot_id": ASSISTANT_ID
    }
    
    print("\nCreating a widget session...")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        session_id = response.json()["session_id"]
        print(f"✅ Widget session created. Session ID: {session_id}")
        
        # Send a message to the widget
        url = f"{BASE_URL}/api/chat/widget"
        data = {
            "session_id": session_id,
            "message": "Hello from the widget test!"
        }
        
        print("Sending a message to the widget...")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("✅ Widget message sent successfully.")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Failed to send widget message. Status: {response.status_code}")
            print(f"Response: {response.text}")
    else:
        print(f"❌ Failed to create widget session. Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    print("=== Testing Chat API ===")
    
    # Test regular API flow
    session_id = test_create_session()
    if session_id:
        test_send_message(session_id)
    
    # Test widget flow
    test_widget_flow()
    
    print("\n=== Test Complete ===")
