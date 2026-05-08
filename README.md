# AI Travel Planning Platform 🌍✈️

A production-grade, AI-powered travel planning system that generates personalized travel itineraries using Google Gemini AI, weather data, and intelligent recommendations.

## ✨ Features

- **🤖 AI-Powered Planning** - Uses Google Gemini 1.5 Flash for intelligent itinerary generation
- **🌦️ Real-time Weather Integration** - Weather-aware recommendations and backup indoor activities
- **💰 Smart Budget Management** - Automatic budget allocation and cost tracking
- **♿ Full Accessibility Support** - WCAG 2.1 AA compliant, keyboard navigation, screen reader support
- **🌐 Multiple UI Options**:
  - Modern responsive web interface with Flask + HTML/CSS/JS
  - Gradio UI for quick interactions
- **📱 Mobile Friendly** - Responsive design works on all devices
- **🔒 Security First** - Input validation, error handling, secure API design
- **🧪 Well-Tested** - Comprehensive unit and integration tests
- **📊 Production Ready** - Docker support, CI/CD configs, monitoring logs

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API Key (Get it from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/P-KamalTeja/PromptWars.git
   cd PromptWars
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

### Running the Application

#### Web UI (Recommended)
```bash
python main.py --ui web
# Visit http://localhost:8080
```

#### Gradio UI
```bash
python main.py --ui gradio
# Visit the URL shown in terminal
```

#### With Options
```bash
python main.py --ui web --host 0.0.0.0 --port 8080 --debug
python main.py --ui gradio --share  # Create shareable link
```

## 📁 Project Structure

```
PromptWars/
├── src/
│   ├── core/                    # Core infrastructure
│   │   ├── config.py           # Configuration management
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logger.py           # Logging setup
│   │   └── __init__.py
│   │
│   ├── models/                  # Data models & validation
│   │   ├── __init__.py         # Data classes
│   │   ├── validator.py        # Input validation
│   │
│   ├── services/                # External services
│   │   ├── gemini_service.py   # Google Gemini integration
│   │   ├── weather_service.py  # Weather API integration
│   │   └── __init__.py
│   │
│   ├── api/                     # Business logic
│   │   ├── trip_engine.py      # Trip planning engine
│   │   ├── rest_api.py         # REST API endpoints
│   │   └── __init__.py
│   │
│   └── ui/                      # User interfaces
│       ├── gradio_ui.py        # Gradio interface
│       ├── web_ui.py           # Flask web interface
│       ├── templates/
│       │   └── index.html      # Web UI template
│       ├── static/
│       │   ├── css/            # Stylesheets
│       │   └── js/             # JavaScript files
│       └── __init__.py
│
├── tests/                       # Test suite
│   ├── unit/
│   ├── integration/
│   └── test_core.py
│
├── config/                      # Configuration files
├── main.py                      # Application entry point
├── Dockerfile                   # Docker configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── cloudbuild.yaml              # Cloud Build config
└── README.md                    # This file
```

## 🛠️ Configuration

### Environment Variables

Create `.env` file with:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
GOOGLE_MAPS_API_KEY=your_maps_key
GOOGLE_CLOUD_PROJECT=your_project_id
USE_FIRESTORE=false
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8080
ENABLE_WEATHER=true
ENABLE_CACHING=true
```

## 🧪 Testing

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

Run specific test:
```bash
pytest tests/test_core.py::TestInputValidator -v
```

## 🐳 Docker Deployment

### Build image
```bash
docker build -t travel-planner:latest .
```

### Run container
```bash
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key \
  travel-planner:latest
```

### Using Docker Compose
```bash
docker-compose up
```

## ☁️ Cloud Deployment

### Google Cloud Build

The project includes `cloudbuild.yaml` for automated deployment:

```bash
gcloud builds submit --config=cloudbuild.yaml
```

### Cloud Run
```bash
gcloud run deploy travel-planner \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars=GEMINI_API_KEY=your_key
```

## 📚 API Documentation

### REST Endpoints

#### Plan Trip
```
POST /api/v1/trips/plan
Content-Type: application/json

{
  "destination": "Paris",
  "start_date": "2024-06-01",
  "end_date": "2024-06-05",
  "budget": 2000,
  "travelers": 2,
  "traveler_type": "couple",
  "preferences": ["cultural", "adventure"],
  "interests": ["museums", "food", "art"]
}

Response: 201 Created
{
  "trip_id": "uuid",
  "destination": {...},
  "total_cost": 2000,
  "daily_itineraries": [...]
}
```

#### Get Trip
```
GET /api/v1/trips/{trip_id}

Response: 200 OK
{trip_details}
```

#### Update Trip
```
POST /api/v1/trips/{trip_id}/update
Content-Type: application/json

{
  "update_request": "Add more museums and reduce budget"
}

Response: 200 OK
{updated_trip_details}
```

## ♿ Accessibility Features

- ✅ WCAG 2.1 Level AA compliance
- ✅ Keyboard navigation support
- ✅ Screen reader optimized
- ✅ High contrast mode support
- ✅ Reduced motion support
- ✅ Proper heading hierarchy
- ✅ Color blind friendly
- ✅ Touch-friendly interface

## 🔒 Security

- Input validation on all endpoints
- Secure error handling
- Rate limiting ready
- CORS support
- Environment-based configuration
- No credentials in code
- SQL injection prevention
- XSS protection

## 📊 Logging

Structured JSON logging with:
- Request/response tracking
- Error logging with context
- Performance metrics
- User activity logs

View logs:
```bash
tail -f logs/app.log | jq .
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📝 Code Quality

- **Linting**: `flake8 src/`
- **Formatting**: `black src/`
- **Type Checking**: `mypy src/`
- **Import Sorting**: `isort src/`

Run all quality checks:
```bash
black src/ && isort src/ && flake8 src/ && mypy src/
```

## 🐛 Troubleshooting

### API Key Issues
```
Error: GEMINI_API_KEY environment variable is required
→ Set GEMINI_API_KEY in .env file
```

### Port Already in Use
```bash
python main.py --port 8081
```

### Import Errors
```bash
pip install -r requirements.txt --force-reinstall
```

### Weather Service Timeout
- Service disabled by default, enable with `ENABLE_WEATHER=true`
- Timeout set to 10 seconds

## 📈 Performance

- Response time: < 5 seconds for itinerary generation
- Supports concurrent requests
- Caching enabled by default (3600s TTL)
- Optimized for mobile

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] User accounts and saved trips
- [ ] Social sharing features
- [ ] Integration with booking APIs
- [ ] Mobile app
- [ ] Advanced traffic integration
- [ ] Event recommendations

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini AI for powerful LLM capabilities
- Gradio for easy UI creation
- Weather data from wttr.in
- Community contributions

## 📞 Support

- Issues: [GitHub Issues](https://github.com/P-KamalTeja/PromptWars/issues)
- Email: support@travelplanner.ai
- Documentation: [Full Docs](https://github.com/P-KamalTeja/PromptWars/wiki)

---

**Made with ❤️ for travelers worldwide**
