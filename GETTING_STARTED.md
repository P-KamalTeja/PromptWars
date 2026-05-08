# 🚀 Getting Started Guide

## Quick Setup (5 minutes)

### 1️⃣ Prerequisites
- Python 3.9 or higher
- Google Gemini API Key ([Get it free](https://aistudio.google.com/app/apikey))

### 2️⃣ Clone & Setup

**Windows:**
```bash
git clone https://github.com/P-KamalTeja/PromptWars.git
cd PromptWars
setup.bat
```

**macOS/Linux:**
```bash
git clone https://github.com/P-KamalTeja/PromptWars.git
cd PromptWars
chmod +x setup.sh
./setup.sh
```

### 3️⃣ Configure API Key

Edit `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
```

### 4️⃣ Run Application

**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
./run.sh
```

Then select:
- **Option 1** → Modern Web UI (Recommended)
- **Option 2** → Gradio UI

Visit: **http://localhost:8080**

---

## Features Overview

### 🌐 Web Interface
- Clean, modern design
- Full responsive mobile support
- Dark/light mode
- Keyboard navigation
- Screen reader support

### 🎯 Trip Planning
1. **Enter Destination** - Any city or region
2. **Set Budget** - $100 to $1,000,000
3. **Choose Duration** - 1-30 days
4. **Add Interests** - Museums, hiking, food, etc.
5. **Get Itinerary** - AI generates personalized plan

### ✏️ Update Trips
- Get your Trip ID from first plan
- Make changes anytime
- AI adapts your itinerary instantly

---

## Customization

### Change Port
```bash
python main.py --ui web --port 3000
```

### Debug Mode
```bash
python main.py --ui web --debug
```

### Gradio with Share Link
```bash
python main.py --ui gradio --share
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GEMINI_API_KEY | ✅ Yes | - | Google Gemini API key |
| DEBUG | No | false | Enable debug mode |
| LOG_LEVEL | No | INFO | Logging level |
| ENABLE_WEATHER | No | true | Weather integration |
| ENABLE_CACHING | No | true | Response caching |

---

## Troubleshooting

### ❌ "GEMINI_API_KEY not set"
→ Add your API key to `.env` file

### ❌ "Port 8080 already in use"
→ Use different port: `python main.py --ui web --port 8081`

### ❌ Module import errors
→ Reinstall: `pip install -r requirements.txt --force-reinstall`

### ❌ Virtual environment issues
→ Delete `venv` folder and run setup again

---

## First Usage Example

1. **Open Web UI** → http://localhost:8080
2. **Fill form:**
   - Destination: "Tokyo"
   - Budget: "$2000"
   - Duration: "5 days"
   - Interests: "Temples, Food, Shopping"
   - Travelers: "2"
   - Type: "Couple"
3. **Click "Generate Itinerary"**
4. **Get your Trip ID** - Save it!
5. **Update anytime** - Use Trip ID in "Update" tab

---

## Next Steps

- 📚 Read [Full Documentation](README.md)
- 🧪 Run tests: `pytest tests/`
- 🐳 Deploy with Docker
- 📤 Push to GitHub
- ☁️ Deploy to Cloud Run

---

**Happy Travels! 🌍✈️**
