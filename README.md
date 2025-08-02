# SaaS AI Chatbot Backend

This is the backend service for the SaaS AI Chatbot application. It provides API endpoints for managing chat sessions and processing messages using OpenRouter AI.

## Features

- Create chat sessions
- Process chat messages
- Widget integration support
- Supabase database integration
- OpenRouter AI integration

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/majd444/probable-pancake.git
   cd probable-pancake/backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your environment variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `OPENROUTER_API_KEY`: Your OpenRouter API key

## License

MIT Chatbot SaaS Backend

This is the backend service for the AI Chatbot SaaS platform, built with FastAPI, Supabase, and OpenRouter.

## Features

- Create and manage chat sessions
- Process chat messages with OpenRouter's AI models
- Widget support for easy website integration
- Session management and conversation history
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Supabase account and project
- OpenRouter API key

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your Supabase and OpenRouter credentials

## Running the Server

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Create a Chat Session
```
POST /api/chat/session
```

### Send a Chat Message
```
POST /api/chat
```

### Create a Widget Session
```
POST /api/chat/widget/session
```

### Send a Widget Chat Message
```
POST /api/chat/widget
```

### Health Check
```
GET /health
```

## Database Schema

### Tables

#### `chatbots`
- `id` (uuid, primary key)
- `api_key` (text)
- `model_name` (text)
- `created_at` (timestamp)
- `updated_at` (timestamp)

#### `sessions`
- `session_id` (uuid, primary key)
- `chatbot_id` (uuid, foreign key to chatbots.id)
- `created_at` (timestamp)
- `last_activity` (timestamp)
- `is_active` (boolean)
- `is_widget` (boolean, default: false)

#### `conversations`
- `id` (serial, primary key)
- `session_id` (uuid, foreign key to sessions.session_id)
- `role` (text, enum: 'user' or 'assistant')
- `content` (text)
- `timestamp` (timestamp)

## Deployment

### Heroku

1. Install the Heroku CLI and login
2. Create a new Heroku app
3. Set environment variables:
   ```bash
   heroku config:set SUPABASE_URL=your_supabase_url
   heroku config:set SUPABASE_KEY=your_supabase_key
   heroku config:set OPENROUTER_API_KEY=your_openrouter_key
   ```
4. Deploy your code

### Docker

1. Build the Docker image:
   ```bash
   docker build -t ai-chatbot-backend .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env ai-chatbot-backend
   ```

## License

This project is licensed under the MIT License.
