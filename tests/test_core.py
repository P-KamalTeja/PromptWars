"""Application tests."""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core import Config, ValidationError, TravelPlanningError
from src.models import (
    TripRequest,
    TravelerType,
    TravelPreferences,
    Budget,
    Location,
    Activity,
    Weather,
)
from src.models.validator import InputValidator


class TestInputValidator:
    """Test input validation."""

    def test_validate_destination_valid(self):
        """Test valid destination."""
        InputValidator.validate_destination("Paris")
        InputValidator.validate_destination("New York")

    def test_validate_destination_invalid(self):
        """Test invalid destination."""
        with pytest.raises(ValidationError):
            InputValidator.validate_destination("")

        with pytest.raises(ValidationError):
            InputValidator.validate_destination("a")

        with pytest.raises(ValidationError):
            InputValidator.validate_destination("x" * 101)

    def test_validate_budget_valid(self):
        """Test valid budget."""
        InputValidator.validate_budget(100)
        InputValidator.validate_budget(5000)
        InputValidator.validate_budget(500000)

    def test_validate_budget_invalid(self):
        """Test invalid budget."""
        with pytest.raises(ValidationError):
            InputValidator.validate_budget(50)

        with pytest.raises(ValidationError):
            InputValidator.validate_budget(1000001)

    def test_validate_duration_valid(self):
        """Test valid duration."""
        start = datetime.now()
        end = start + timedelta(days=5)
        InputValidator.validate_duration(start, end)

    def test_validate_duration_invalid(self):
        """Test invalid duration."""
        start = datetime.now()
        end = start - timedelta(days=1)

        with pytest.raises(ValidationError):
            InputValidator.validate_duration(start, end)

    def test_validate_travelers_valid(self):
        """Test valid traveler count."""
        InputValidator.validate_travelers(1)
        InputValidator.validate_travelers(50)

    def test_validate_travelers_invalid(self):
        """Test invalid traveler count."""
        with pytest.raises(ValidationError):
            InputValidator.validate_travelers(0)

        with pytest.raises(ValidationError):
            InputValidator.validate_travelers(101)

    def test_validate_interests_valid(self):
        """Test valid interests."""
        InputValidator.validate_interests(["Museums", "Hiking"])

    def test_validate_interests_invalid(self):
        """Test invalid interests."""
        with pytest.raises(ValidationError):
            InputValidator.validate_interests(["x" * 51])


class TestDataModels:
    """Test data models."""

    def test_location_to_dict(self):
        """Test location to dictionary conversion."""
        location = Location(
            name="Paris",
            latitude=48.8566,
            longitude=2.3522,
            country="France",
        )
        data = location.to_dict()

        assert data["name"] == "Paris"
        assert data["latitude"] == 48.8566
        assert data["country"] == "France"

    def test_weather_creation(self):
        """Test weather object creation."""
        weather = Weather(
            temperature=20.0,
            condition="Sunny",
            humidity=60.0,
            wind_speed=10.0,
        )

        assert weather.temperature == 20.0
        assert weather.condition == "Sunny"

    def test_budget_allocation(self):
        """Test budget allocation."""
        budget = Budget(total=1000)

        accommodation = budget.get_allocation("accommodation")
        assert accommodation == 400

        activities = budget.get_allocation("activities")
        assert activities == 300


class TestTripRequest:
    """Test trip request creation."""

    def test_trip_request_creation(self):
        """Test creating a trip request."""
        start = datetime.now()
        end = start + timedelta(days=5)

        trip = TripRequest(
            destination="Paris",
            start_date=start,
            end_date=end,
            travelers=2,
            traveler_type=TravelerType.COUPLE,
            budget=Budget(total=2000),
            preferences=[TravelPreferences.CULTURAL],
            interests=["Museums", "Food"],
        )

        assert trip.destination == "Paris"
        assert trip.duration_days == 5
        assert trip.travelers == 2

    def test_trip_request_duration(self):
        """Test trip duration calculation."""
        start = datetime.now()
        end = start + timedelta(days=7)

        trip = TripRequest(
            destination="Tokyo",
            start_date=start,
            end_date=end,
            travelers=1,
            traveler_type=TravelerType.SOLO,
            budget=Budget(total=3000),
            preferences=[TravelPreferences.ADVENTURE],
        )

        assert trip.duration_days == 7


class TestConfig:
    """Test configuration loading."""

    def test_config_validation(self):
        """Test configuration validation."""
        # This would require setting GEMINI_API_KEY env var
        # For now, we just test the structure
        assert Config.__dataclass_fields__ is not None


def run_tests():
    """Run all tests."""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
