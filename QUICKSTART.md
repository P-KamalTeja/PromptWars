# 🚀 QUICK REFERENCE

## First Time Setup (Choose 1)

### Windows
```bash
setup.bat
```

### macOS/Linux
```bash
chmod +x setup.sh
./setup.sh
```

---

## Run Application (Choose 1)

### Windows
```bash
run.bat
# Then choose: 1 (Web UI) or 2 (Gradio UI)
```

### macOS/Linux
```bash
./run.sh
# Then choose: 1 (Web UI) or 2 (Gradio UI)
```

### Manual (Any OS)
```bash
# Activate virtual environment
source venv/bin/activate    # macOS/Linux
# or
venv\Scripts\activate       # Windows

# Web UI (Recommended)
python main.py --ui web

# Gradio UI
python main.py --ui gradio

# Both on different ports
python main.py --ui web --port 8080 &
python main.py --ui gradio --port 7860
```

---

## Access Application

- **Web UI:** http://localhost:8080
- **Gradio UI:** http://localhost:7860
- **API:** http://localhost:8080/api/v1

---

## Usage Example

1. **Plan Trip**
   - Destination: `Tokyo`
   - Budget: `$3000`
   - Duration: `7 days`
   - Interests: `Temples, Food, Shopping`
   - Travelers: `2`
   - Type: `Couple`
   - Click "Generate Itinerary"

2. **Save Your Trip ID** - Copy the Trip ID from results

3. **Update Anytime**
   - Paste Trip ID in "Update" tab
   - Describe changes
   - Click "Update Itinerary"

---

## Common Commands

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/

# Docker build
docker build -t travel-planner:latest .

# Docker run
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key \
  travel-planner:latest
```

---

## Environment Setup

**Edit `.env` file:**
```env
GEMINI_API_KEY=your_api_key_here
DEBUG=false
LOG_LEVEL=INFO
```

**Get API Key:** https://aistudio.google.com/app/apikey

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API Key Error | Add GEMINI_API_KEY to .env |
| Port in use | Change port: `python main.py --port 8081` |
| Import errors | Reinstall: `pip install -r requirements.txt --force-reinstall` |
| Virtual env issues | Delete venv folder and run setup again |

---

## Documentation Files

- 📖 **[README.md](README.md)** - Full documentation
- 📚 **[GETTING_STARTED.md](GETTING_STARTED.md)** - Detailed setup
- 👨‍💻 **[DEVELOPMENT.md](DEVELOPMENT.md)** - Dev guide
- 📡 **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API specs
- 📊 **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview

---

## Features

✅ AI-powered trip planning  
✅ Modern web interface  
✅ Gradio UI  
✅ Real-time weather  
✅ Budget management  
✅ Full accessibility  
✅ REST API  
✅ Docker ready  

---

## Support

- 🐛 Report issues on GitHub
- 📧 Contact: support@travelplanner.ai
- 💬 Join our community

---

**Happy Travels! 🌍✈️**
