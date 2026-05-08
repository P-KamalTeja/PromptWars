#!/bin/bash
# Development setup script for Unix/Linux/macOS

set -e

echo "🚀 Setting up AI Travel Platform..."

# Check Python version
echo "📌 Checking Python version..."
python3 --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Setup environment
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file - please edit and add your GEMINI_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v --tb=short

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your GEMINI_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the app: python main.py --ui web"
echo ""
