@echo off
REM Chat Application Backend - Startup Script for Windows

echo 🚀 Starting Chat Application Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo ⚠️  Please edit .env with your database credentials before running!
    pause
    exit /b 1
)

REM Initialize database
echo 🗄️  Initializing database...
python init_db.py

REM Start the server
echo 🌐 Starting server on http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
