#!/bin/bash
# Quick run script - assumes setup is already done

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please run setup.sh first"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d venv ]; then
    source venv/bin/activate
fi

echo -e "${BLUE}🌍 AI Travel Platform${NC}"
echo ""
echo "Select UI to launch:"
echo "1) Web UI (Modern responsive interface)"
echo "2) Gradio UI (Simple interactive interface)"
echo "3) Both (Run on different ports)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Starting Web UI on http://localhost:8080${NC}"
        python main.py --ui web
        ;;
    2)
        echo -e "${GREEN}🚀 Starting Gradio UI${NC}"
        python main.py --ui gradio
        ;;
    3)
        echo -e "${GREEN}🚀 Starting Web UI on http://localhost:8080${NC}"
        python main.py --ui web --port 8080 &
        sleep 2
        echo -e "${GREEN}🚀 Starting Gradio UI${NC}"
        python main.py --ui gradio --port 7860
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
