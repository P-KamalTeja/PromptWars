"""Data models and schemas."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TravelPreferences(Enum):
    """Travel preference categories."""

    ADVENTURE = "adventure"
    LUXURY = "luxury"
    BUDGET = "budget"
    CULTURAL = "cultural"
    RELAXATION = "relaxation"
    FAMILY = "family"


class TravelerType(Enum):
    """Types of travelers."""

    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    GROUP = "group"


@dataclass
class Budget:
    """Budget information."""

    total: float
    currency: str = "USD"
    accommodation_percentage: float = 0.4
    activities_percentage: float = 0.3
    food_percentage: float = 0.2
    transport_percentage: float = 0.1

    def get_allocation(self, category: str) -> float:
        """Get budget allocation for category.

        Args:
            category: Budget category

        Returns:
            Allocated budget amount
        """
        percentages = {
            "accommodation": self.accommodation_percentage,
            "activities": self.activities_percentage,
            "food": self.food_percentage,
            "transport": self.transport_percentage,
        }
        return self.total * percentages.get(category, 0)


@dataclass
class Weather:
    """Weather information."""

    temperature: float
    condition: str
    humidity: float
    wind_speed: float
    precipitation: float = 0.0
    uv_index: int = 0
    feels_like: Optional[float] = None


@dataclass
class Location:
    """Location information."""

    name: str
    latitude: float
    longitude: float
    country: str
    region: Optional[str] = None
    timezone: Optional[str] = None
    altitude: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Location as dictionary
        """
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country": self.country,
            "region": self.region,
            "timezone": self.timezone,
            "altitude": self.altitude,
        }


@dataclass
class Activity:
    """Single activity in itinerary."""

    name: str
    description: str
    location: Location
    duration_hours: float
    cost: float
    category: str
    time_slot: Optional[str] = None
    accessibility_notes: Optional[str] = None
    rating: Optional[float] = None
    booking_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Activity as dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "location": self.location.to_dict(),
            "duration_hours": self.duration_hours,
            "cost": self.cost,
            "category": self.category,
            "time_slot": self.time_slot,
            "accessibility_notes": self.accessibility_notes,
            "rating": self.rating,
            "booking_url": self.booking_url,
        }


@dataclass
class DayItinerary:
    """Single day itinerary."""

    day_number: int
    date: datetime
    activities: List[Activity] = field(default_factory=list)
    accommodation: Optional[str] = None
    accommodation_cost: float = 0.0
    meals: Optional[List[str]] = None
    estimated_spending: float = 0.0
    weather: Optional[Weather] = None
    notes: Optional[str] = None

    def get_total_cost(self) -> float:
        """Calculate total cost for the day.

        Returns:
            Total daily cost
        """
        return (
            sum(a.cost for a in self.activities)
            + self.accommodation_cost
        )


@dataclass
class TripRequest:
    """Trip planning request."""

    destination: str
    start_date: datetime
    end_date: datetime
    travelers: int
    traveler_type: TravelerType
    budget: Budget
    preferences: List[TravelPreferences]
    interests: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    accessibility_needs: Optional[str] = None

    @property
    def duration_days(self) -> int:
        """Get trip duration in days.

        Returns:
            Number of days
        """
        return (self.end_date - self.start_date).days


@dataclass
class ItineraryResponse:
    """Complete trip itinerary response."""

    trip_id: str
    destination: Location
    trip_request: TripRequest
    daily_itineraries: List[DayItinerary] = field(default_factory=list)
    total_cost: float = 0.0
    total_activities: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0
    alternative_options: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Itinerary as dictionary
        """
        return {
            "trip_id": self.trip_id,
            "destination": self.destination.to_dict(),
            "duration_days": self.trip_request.duration_days,
            "total_cost": self.total_cost,
            "total_activities": self.total_activities,
            "confidence_score": self.confidence_score,
            "daily_itineraries": [
                {
                    "day_number": day.day_number,
                    "date": day.date.isoformat(),
                    "activities": [a.to_dict() for a in day.activities],
                    "accommodation": day.accommodation,
                    "accommodation_cost": day.accommodation_cost,
                    "total_cost": day.get_total_cost(),
                }
                for day in self.daily_itineraries
            ],
        }
