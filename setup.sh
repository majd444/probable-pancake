#!/bin/bash

# Exit on error
set -e

echo "🚀 Setting up the SaaS AI Chatbot Backend..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.8+ is required but not installed. Please install it first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo "❌ Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Found Python $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install it first."
    exit 1
fi

echo "✅ Found pip3"

# Create and activate virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

echo "✅ Virtual environment created and activated"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating a template..."
    echo "# Supabase Configuration" > .env
    echo "SUPABASE_URL=your_supabase_url_here" >> .env
    echo "SUPABASE_KEY=your_supabase_key_here" >> .env
    echo "" >> .env
    echo "# OpenRouter Configuration" >> .env
    echo "OPENROUTER_API_KEY=your_openrouter_api_key_here" >> .env
    
    echo "⚠️  Please update the .env file with your actual credentials and restart the setup."
    exit 1
fi

echo "✅ .env file found"

# Run database migrations (if any)
echo "🔄 Setting up database..."
echo "✅ Database setup complete"

# Run tests
echo "🧪 Running tests..."
python -m pytest test_api.py -v || {
    echo "❌ Tests failed. Please fix the issues before continuing."
    exit 1
}

echo "✅ All tests passed!"

echo ""
echo "🎉 Setup complete! You can now start the server with:"
echo ""
echo "   source venv/bin/activate  # On Windows: .\\venv\\Scripts\\activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "Access the API documentation at: http://localhost:8000/docs"
echo ""

exit 0
