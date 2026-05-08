"""Tests for the Flask web UI."""
from src.core import Config
from src.ui.web_ui import WebUI


def create_client():
    """Create a test client without initializing Gemini."""
    config = Config(GEMINI_API_KEY="test-key", ENABLE_WEATHER=False)
    return WebUI(config).app.test_client()


def test_health_endpoint_returns_ok():
    """Health endpoint should be lightweight and reliable."""
    response = create_client().get("/health")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "OK"


def test_index_page_loads_with_security_headers():
    """Landing page should render and include baseline security headers."""
    response = create_client().get("/")

    assert response.status_code == 200
    assert "AI Travel Planner" in response.get_data(as_text=True)
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_unknown_route_stays_404():
    """Global error handler should not convert missing pages to 500."""
    response = create_client().get("/missing")

    assert response.status_code == 404


def test_plan_requires_json_body():
    """Trip planning should reject malformed requests before touching Gemini."""
    response = create_client().post("/api/plan", data="not-json")

    assert response.status_code == 400
    assert response.get_json()["error"] == "JSON request body is required"
