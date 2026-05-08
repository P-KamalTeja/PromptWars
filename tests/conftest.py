"""Test configuration and fixtures."""
import pytest

from src.core import Config


@pytest.fixture
def test_config():
    """Provide test configuration."""
    import os
    os.environ["GEMINI_API_KEY"] = "test-key-12345"
    return Config.from_env()


@pytest.fixture
def test_trip_data():
    """Provide sample trip data."""
    from datetime import datetime, timedelta
    from src.models import (
        TripRequest,
        TravelerType,
        TravelPreferences,
        Budget,
    )

    start = datetime.now()
    end = start + timedelta(days=5)

    return TripRequest(
        destination="Paris",
        start_date=start,
        end_date=end,
        travelers=2,
        traveler_type=TravelerType.COUPLE,
        budget=Budget(total=2000),
        preferences=[TravelPreferences.CULTURAL],
        interests=["museums", "food"],
    )
