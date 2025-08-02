#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
fi

# Install dependencies if not already installed
if [ ! -d "venv" ] || [ "$1" == "--install" ]; then
    echo "📦 Installing dependencies..."
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
fi

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run database initialization
echo "🔧 Initializing database..."
python init_db.py

# Run the FastAPI server
echo "🚀 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
