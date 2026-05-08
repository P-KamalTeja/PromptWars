"""Core trip planning engine."""
import uuid
from typing import TYPE_CHECKING
from typing import Dict, Optional
from datetime import datetime, timedelta

from src.core import Config, get_logger, TravelPlanningError
from src.models import (
    DayItinerary,
    ItineraryResponse,
    Location,
    TripRequest,
    Weather,
)
from src.models.validator import InputValidator
from src.services.weather_service import WeatherService

if TYPE_CHECKING:
    from src.services.gemini_service import GeminiService


logger = get_logger(__name__)


class TripPlanningEngine:
    """Main trip planning orchestration engine."""

    def __init__(self, config: Config):
        """Initialize trip planning engine.

        Args:
            config: Application configuration
        """
        self.config = config
        self._gemini_service: Optional["GeminiService"] = None
        self.weather_service = WeatherService(config)
        self.trip_cache: Dict[str, ItineraryResponse] = {}

    @property
    def gemini_service(self) -> "GeminiService":
        """Create Gemini service only when AI generation is needed."""
        if self._gemini_service is None:
            from src.services.gemini_service import GeminiService

            self._gemini_service = GeminiService(self.config)
        return self._gemini_service

    def plan_trip(self, trip_request: TripRequest) -> ItineraryResponse:
        """Create a complete trip itinerary.

        Args:
            trip_request: Trip planning request

        Returns:
            Generated itinerary response

        Raises:
            TravelPlanningError: If planning fails
        """
        try:
            # Validate request
            InputValidator.validate_trip_request(trip_request)
            logger.info(f"Planning trip to {trip_request.destination}")

            # Get weather data, but do not fail the whole trip if it is unavailable.
            try:
                weather = self.weather_service.get_weather(trip_request.destination)
            except Exception:
                logger.exception("Weather lookup failed; continuing without weather")
                weather = None

            # Generate itinerary with AI. If Gemini is not configured or unavailable,
            # still return a structured starter itinerary so the UI remains usable.
            try:
                itinerary_text = self.gemini_service.generate_itinerary(
                    trip_request,
                    weather,
                )
            except Exception:
                logger.exception("Gemini itinerary generation failed")
                itinerary_text = self._build_fallback_itinerary(trip_request)

            # Parse and structure itinerary
            trip_id = str(uuid.uuid4())
            itinerary = self._parse_itinerary(
                trip_id, trip_request, itinerary_text, weather
            )

            # Cache the result
            if self.config.ENABLE_CACHING:
                self.trip_cache[trip_id] = itinerary

            logger.info(f"Trip planning completed: {trip_id}")
            return itinerary

        except Exception as e:
            logger.error(f"Trip planning failed: {str(e)}")
            raise TravelPlanningError(f"Failed to plan trip: {str(e)}")

    def update_trip(
        self, trip_id: str, update_request: str
    ) -> Optional[ItineraryResponse]:
        """Update an existing trip.

        Args:
            trip_id: Existing trip ID
            update_request: User's update request

        Returns:
            Updated itinerary or None if not found

        Raises:
            TravelPlanningError: If update fails
        """
        try:
            # Try to get from cache first
            existing_trip = self.trip_cache.get(trip_id)
            if not existing_trip:
                logger.warning(f"Trip {trip_id} not found in cache")
                return None

            # Convert to text for AI processing
            existing_text = self._format_itinerary_for_update(existing_trip)

            # Get updated itinerary from AI, or keep the existing plan if unavailable.
            try:
                updated_text = self.gemini_service.update_itinerary(
                    session_id=trip_id,
                    user_request=update_request,
                    existing_plan=existing_text,
                )
            except Exception:
                logger.exception("Gemini itinerary update failed")
                updated_text = existing_text

            # Parse updated itinerary
            updated_trip = self._parse_itinerary(
                trip_id,
                existing_trip.trip_request,
                updated_text,
                None,
            )
            updated_trip.updated_at = datetime.utcnow()

            # Update cache
            self.trip_cache[trip_id] = updated_trip

            logger.info(f"Trip {trip_id} updated successfully")
            return updated_trip

        except Exception as e:
            logger.error(f"Trip update failed: {str(e)}")
            raise TravelPlanningError(f"Failed to update trip: {str(e)}")

    def get_trip(self, trip_id: str) -> Optional[ItineraryResponse]:
        """Retrieve a cached trip.

        Args:
            trip_id: Trip identifier

        Returns:
            Trip itinerary or None
        """
        return self.trip_cache.get(trip_id)

    @staticmethod
    def _build_fallback_itinerary(trip_request: TripRequest) -> str:
        """Build a simple fallback itinerary when AI generation is unavailable."""
        lines = [f"Trip plan for {trip_request.destination}"]
        interests = ", ".join(trip_request.interests) or "local highlights"

        for day in range(1, trip_request.duration_days + 1):
            lines.extend(
                [
                    f"Day {day}",
                    "Morning: Start after breakfast and visit one nearby "
                    "popular attraction at a relaxed pace.",
                    f"Afternoon: Spend time on {interests}. Take breaks, "
                    "drink water, and avoid rushing.",
                    "Evening: Have dinner close to your stay and review the "
                    "next day's plan.",
                ]
            )

        return "\n".join(lines)

    @staticmethod
    def _parse_itinerary(
        trip_id: str,
        trip_request: TripRequest,
        itinerary_text: str,
        weather: Optional[Weather] = None,
    ) -> ItineraryResponse:
        """Parse AI-generated itinerary text into structured format.

        Args:
            trip_id: Unique trip identifier
            trip_request: Original request
            itinerary_text: AI-generated itinerary
            weather: Weather data

        Returns:
            Structured itinerary response
        """
        try:
            # Create destination location
            destination = Location(
                name=trip_request.destination,
                latitude=0.0,  # Would be fetched from Maps API
                longitude=0.0,
                country="",  # Would be fetched from Maps API
            )

            # Create itinerary response
            itinerary = ItineraryResponse(
                trip_id=trip_id,
                destination=destination,
                trip_request=trip_request,
                total_cost=trip_request.budget.total,
            )
            itinerary.alternative_options.append(
                {
                    "title": "Detailed itinerary",
                    "description": itinerary_text,
                }
            )

            # Parse day-by-day activities from text
            # This is simplified - in production would use more sophisticated parsing
            current_day = 1
            for day_num in range(trip_request.duration_days):
                day_date = trip_request.start_date + timedelta(days=day_num)

                day_itinerary = DayItinerary(
                    day_number=current_day,
                    date=day_date,
                    weather=weather,
                )

                itinerary.daily_itineraries.append(day_itinerary)
                current_day += 1

            # Set confidence based on various factors
            # Would be calculated from data quality signals in production.
            itinerary.confidence_score = 0.85

            logger.debug(
                "Parsed itinerary with %s days",
                len(itinerary.daily_itineraries),
            )
            return itinerary

        except Exception as e:
            logger.error(f"Failed to parse itinerary: {str(e)}")
            raise TravelPlanningError(f"Failed to parse itinerary: {str(e)}")

    @staticmethod
    def _format_itinerary_for_update(itinerary: ItineraryResponse) -> str:
        """Format itinerary for AI processing during updates.

        Args:
            itinerary: Structured itinerary

        Returns:
            Formatted text representation
        """
        lines = [
            f"# Trip to {itinerary.destination.name}",
            f"Duration: {itinerary.trip_request.duration_days} days",
            f"Budget: ${itinerary.total_cost}",
            "",
        ]

        for day in itinerary.daily_itineraries:
            lines.append(f"## Day {day.day_number} ({day.date.strftime('%Y-%m-%d')})")
            lines.append(f"Accommodation: {day.accommodation or 'TBD'}")
            lines.append(f"Cost: ${day.get_total_cost()}")
            lines.append("")

        return "\n".join(lines)
