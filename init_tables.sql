-- Drop tables if they exist
DROP TABLE IF EXISTS public.conversations;
DROP TABLE IF EXISTS public.sessions;
DROP TABLE IF EXISTS public.chatbots;

-- Create the chatbots table
CREATE TABLE public.chatbots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    model_name TEXT NOT NULL,
    api_key TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the sessions table
CREATE TABLE public.sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Create the conversations table
CREATE TABLE public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.sessions(session_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on session_id for faster lookups
CREATE INDEX idx_conversations_session_id ON public.conversations(session_id);

-- Insert a test chatbot
INSERT INTO public.chatbots (id, name, description, model_name, api_key)
VALUES (
    'e97f4988-4f70-470b-b2e5-aca28ddbcff0',
    'Test Chatbot',
    'A test chatbot for development',
    'gpt-3.5-turbo',
    'c8bc40f2-e83d-4e92-ac2b-d5bd6444da0a'
);
