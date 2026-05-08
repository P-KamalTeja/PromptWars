@echo off
REM Development setup script for Windows

echo.
echo 🚀 Setting up AI Travel Platform...
echo.

REM Check Python version
echo 📌 Checking Python version...
python --version

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📥 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Setup environment
echo ⚙️  Setting up environment...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file - please edit and add your GEMINI_API_KEY
) else (
    echo ✅ .env file already exists
)

REM Create directories
echo 📁 Creating necessary directories...
if not exist logs mkdir logs
if not exist data mkdir data

REM Run tests
echo 🧪 Running tests...
pytest tests/ -v --tb=short

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo 1. Edit .env file with your GEMINI_API_KEY
echo 2. Activate virtual environment: venv\Scripts\activate.bat
echo 3. Run the app: python main.py --ui web
echo.
pause
