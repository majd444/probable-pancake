-- Create the chatbots table
CREATE TABLE IF NOT EXISTS public.chatbots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    model_name TEXT NOT NULL,
    api_key TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the sessions table
CREATE TABLE IF NOT EXISTS public.sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chatbot_id UUID NOT NULL REFERENCES public.chatbots(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Create the conversations table
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.sessions(session_id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on session_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON public.conversations(session_id);

-- Enable Row Level Security
ALTER TABLE public.chatbots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;

-- Create policies for chatbots table
CREATE POLICY "Enable read access for all users" ON public.chatbots
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON public.chatbots
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policies for sessions table
CREATE POLICY "Enable read access for all users" ON public.sessions
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON public.sessions
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policies for conversations table
CREATE POLICY "Enable read access for all users" ON public.conversations
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON public.conversations
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');
