#!/bin/bash

# Chat Application Backend - Startup Script

echo "🚀 Starting Chat Application Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your database credentials before running!"
    exit 1
fi

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

# Start the server
echo "🌐 Starting server on http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
