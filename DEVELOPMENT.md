# Development Guide

## Project Architecture

```
Core → Services → Engine → API → UI
 ↓        ↓        ↓       ↓     ↓
Config  Gemini  Engine  REST   Web
Logger  Weather Trip    Flask  Gradio
Errors           Cache
```

## Module Responsibilities

### `src/core/`
- **config.py** - Configuration management, environment loading
- **logger.py** - Structured logging setup
- **exceptions.py** - Custom exception classes

### `src/models/`
- **__init__.py** - Data classes (TripRequest, ItineraryResponse, etc.)
- **validator.py** - Input validation logic

### `src/services/`
- **gemini_service.py** - Google Gemini AI integration
- **weather_service.py** - Weather API integration

### `src/api/`
- **trip_engine.py** - Business logic, trip planning orchestration
- **rest_api.py** - Flask REST API endpoints

### `src/ui/`
- **web_ui.py** - Flask web interface
- **gradio_ui.py** - Gradio interface
- **templates/** - HTML templates
- **static/** - CSS, JavaScript files

---

## Adding New Features

### 1. Add a New Service

Create `src/services/new_service.py`:
```python
from src.core import Config, get_logger

logger = get_logger(__name__)

class NewService:
    def __init__(self, config: Config):
        self.config = config
    
    def do_something(self):
        logger.info("Doing something")
        return result
```

### 2. Add API Endpoint

Edit `src/api/rest_api.py`:
```python
@self.app.route("/api/v1/new-endpoint", methods=["POST"])
def new_endpoint():
    try:
        data = request.get_json()
        result = self.engine.process(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 3. Add UI Component

Edit `src/ui/templates/index.html`:
```html
<section id="new-feature">
    <h2>New Feature</h2>
    <!-- Add your HTML -->
</section>
```

Add JavaScript in `src/ui/static/js/main.js`

---

## Testing

### Unit Tests
```python
# tests/test_core.py
def test_new_feature():
    assert function_works() == expected
```

### Run Tests
```bash
pytest tests/                  # All tests
pytest tests/test_core.py      # Specific file
pytest tests/ -k test_name     # Specific test
pytest tests/ -v --cov=src    # With coverage
```

---

## Code Quality

```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/

# Sort imports
isort src/

# All checks
black src/ && isort src/ && flake8 src/ && mypy src/
```

---

## Debugging

### Enable Debug Mode
```bash
python main.py --debug
```

### View Logs
```bash
tail -f logs/app.log
```

### Use Python Debugger
```python
import pdb; pdb.set_trace()
```

---

## Performance Optimization

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(arg):
    return result
```

### Async Operations
```python
import asyncio

async def fetch_data():
    return await service.get_data()
```

---

## Security Best Practices

1. **Input Validation** - Always validate user input
2. **Error Handling** - Never expose internal errors
3. **Logging** - Don't log sensitive data
4. **Dependencies** - Keep dependencies updated
5. **Secrets** - Use environment variables

---

## Deployment Checklist

- [ ] All tests passing
- [ ] Code formatted with `black`
- [ ] No linting errors with `flake8`
- [ ] Type hints added
- [ ] Documentation updated
- [ ] Environment variables documented
- [ ] Docker image builds
- [ ] Health checks working

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add my feature"

# Push to GitHub
git push origin feature/my-feature

# Create Pull Request on GitHub
```

---

## Common Tasks

### Add Dependency
```bash
pip install package_name
pip freeze > requirements.txt
```

### Create Database Table
```python
# src/db/models.py
class NewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
```

### Add Configuration Option
```python
# src/core/config.py
NEW_OPTION: str = "default_value"
```

---

## Performance Monitoring

View request statistics:
```python
from src.core.logger import log_response

# In endpoint
log_response(logger, status_code, duration_ms)
```

---

## API Rate Limiting

Add rate limiting to `src/api/rest_api.py`:
```python
@app.limit("100 per hour")
def limited_endpoint():
    return result
```

---

## Documentation

- Update README.md for user-facing changes
- Add docstrings to functions
- Keep API docs synchronized
- Document new environment variables

---

**Questions? Open an issue on GitHub!**
