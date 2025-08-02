# SaaS AI Chatbot Backend

This is the backend service for the SaaS AI Chatbot, built with FastAPI, Supabase, and OpenRouter.

## Features

- RESTful API endpoints for chat functionality
- Session management
- Integration with OpenRouter for AI responses
- Supabase for data storage
- CORS enabled for frontend integration

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- A Supabase account and project
- An OpenRouter API key

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables in the `.env` file:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

## Database Setup

1. Create the following tables in your Supabase database:

   ```sql
   -- Chatbots table
   CREATE TABLE public.chatbots (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       api_key TEXT NOT NULL UNIQUE,
       model_name TEXT NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
   );

   -- Sessions table
   CREATE TABLE public.sessions (
       session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
   );

   -- Conversations table
   CREATE TABLE public.conversations (
       id BIGSERIAL PRIMARY KEY,
       session_id UUID NOT NULL REFERENCES public.sessions(session_id) ON DELETE CASCADE,
       role TEXT NOT NULL,
       content TEXT NOT NULL,
       timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
   );
   ```

2. Add a test chatbot:
   ```sql
   INSERT INTO public.chatbots (id, api_key, model_name)
   VALUES ('e97f4988-4f70-470b-b2e5-aca28ddbcff0', 'c8bc40f2-e83d-4e92-ac2b-d5bd6444da0a', 'openai/gpt-3.5-turbo');
   ```

## Running the Application

1. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
2. The API will be available at `http://localhost:8000`
3. Access the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Create a Chat Session
- **URL**: `/api/chat/session`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "api_key": "your_api_key",
    "assistant_id": "your_assistant_id"
  }
  ```
- **Success Response**:
  ```json
  {
    "session_id": "generated-session-id"
  }
  ```

### Send a Chat Message
- **URL**: `/api/chat`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "api_key": "your_api_key",
    "session_id": "session-id",
    "type": "custom_code",
    "assistant_id": "your_assistant_id",
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ]
  }
  ```
- **Success Response**:
  ```json
  {
    "response": "I'm doing well, thank you for asking! How can I assist you today?"
  }
  ```

### Widget Endpoints

#### Create a Widget Session
- **URL**: `/api/chat/widget/session`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "chatbot_id": "your_chatbot_id"
  }
  ```
- **Success Response**:
  ```json
  {
    "session_id": "generated-session-id"
  }
  ```

#### Send a Widget Message
- **URL**: `/api/chat/widget`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "session_id": "session-id",
    "message": "Hello, how are you?"
  }
  ```
- **Success Response**:
  ```json
  {
    "response": "I'm doing well, thank you for asking! How can I assist you today?"
  }
  ```

## Deployment

### Heroku

1. Install the Heroku CLI and login:
   ```bash
   heroku login
   ```

2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

3. Set environment variables on Heroku:
   ```bash
   heroku config:set SUPABASE_URL=your_supabase_url
   heroku config:set SUPABASE_KEY=your_supabase_key
   heroku config:set OPENROUTER_API_KEY=your_openrouter_api_key
   ```

4. Deploy your code:
   ```bash
   git push heroku main
   ```

5. Scale the web process:
   ```bash
   heroku ps:scale web=1
   ```

## Testing

1. Run the test suite:
   ```bash
   # Install test dependencies
   pip install pytest httpx
   
   # Run tests
   pytest
   ```

## License

MIT
