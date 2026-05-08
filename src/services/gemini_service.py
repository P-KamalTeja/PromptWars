"""Google Services integration module."""
import google.generativeai as genai
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.core import Config, get_logger, GoogleServicesError
from src.models import (
    TripRequest,
    ItineraryResponse,
    DayItinerary,
    Activity,
    Location,
    Weather,
)


logger = get_logger(__name__)


class GeminiService:
    """Handles Gemini AI integrations."""

    def __init__(self, config: Config):
        """Initialize Gemini service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.client = None
        self.model = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Gemini client."""
        try:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise GoogleServicesError(
                f"Failed to initialize Gemini: {str(e)}", service="Gemini"
            )

    def generate_itinerary(
        self, trip_request: TripRequest, weather: Optional[Weather] = None
    ) -> str:
        """Generate AI-powered itinerary.

        Args:
            trip_request: Trip planning request
            weather: Current weather data

        Returns:
            Generated itinerary text

        Raises:
            GoogleServicesError: If generation fails
        """
        try:
            prompt = self._build_itinerary_prompt(trip_request, weather)

            response = self.model.generate_content(prompt)
            logger.info(
                f"Successfully generated itinerary for {trip_request.destination}"
            )
            return response.text

        except Exception as e:
            logger.error(f"Itinerary generation failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to generate itinerary: {str(e)}", service="Gemini"
            )

    def update_itinerary(
        self,
        existing_plan: str,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Update existing itinerary based on user feedback.

        Args:
            existing_plan: Current itinerary
            user_request: User's update request
            context: Additional context

        Returns:
            Updated itinerary

        Raises:
            GoogleServicesError: If update fails
        """
        try:
            prompt = f"""You are an expert travel planner AI assistant.

Existing Trip Plan:
{existing_plan}

User's Update Request:
{user_request}

Please update the itinerary to incorporate the user's request while maintaining the overall trip structure and budget constraints. 
Preserve good formatting using markdown.
Suggest alternatives where applicable.
"""

            response = self.model.generate_content(prompt)
            logger.info("Successfully updated itinerary")
            return response.text

        except Exception as e:
            logger.error(f"Itinerary update failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to update itinerary: {str(e)}", service="Gemini"
            )

    def get_recommendations(
        self,
        destination: str,
        preferences: List[str],
        budget: float,
        duration_days: int,
    ) -> Dict[str, Any]:
        """Get personalized recommendations.

        Args:
            destination: Travel destination
            preferences: User preferences
            budget: Total budget
            duration_days: Trip duration

        Returns:
            Recommendations dictionary

        Raises:
            GoogleServicesError: If request fails
        """
        try:
            prompt = f"""Based on the following trip parameters, provide detailed recommendations in JSON format:

Destination: {destination}
Preferences: {', '.join(preferences)}
Budget: ${budget}
Duration: {duration_days} days

Provide recommendations for:
1. Best neighborhoods/areas to stay
2. Top-rated restaurants and cuisines
3. Must-see attractions
4. Local transportation options
5. Hidden gems and local experiences
6. Best time of day to visit attractions
7. Safety tips
8. Local customs and etiquette

Format response as valid JSON."""

            response = self.model.generate_content(prompt)
            logger.info(f"Generated recommendations for {destination}")
            return {"recommendations": response.text}

        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to generate recommendations: {str(e)}", service="Gemini"
            )

    @staticmethod
    def _build_itinerary_prompt(
        trip_request: TripRequest, weather: Optional[Weather] = None
    ) -> str:
        """Build detailed prompt for itinerary generation.

        Args:
            trip_request: Trip planning request
            weather: Current weather

        Returns:
            Formatted prompt
        """
        weather_section = ""
        if weather:
            weather_section = f"""
Current Weather in {trip_request.destination}:
- Temperature: {weather.temperature}°C
- Condition: {weather.condition}
- Humidity: {weather.humidity}%
- Wind Speed: {weather.wind_speed} km/h
- UV Index: {weather.uv_index}
"""

        prompt = f"""You are an expert AI travel planner creating a detailed, personalized travel itinerary.

TRIP DETAILS:
Destination: {trip_request.destination}
Start Date: {trip_request.start_date.strftime('%Y-%m-%d')}
End Date: {trip_request.end_date.strftime('%Y-%m-%d')}
Duration: {trip_request.duration_days} days
Number of Travelers: {trip_request.travelers}
Traveler Type: {trip_request.traveler_type.value}
Total Budget: ${trip_request.budget.total}

PREFERENCES & INTERESTS:
Preferences: {', '.join([p.value for p in trip_request.preferences])}
Interests: {', '.join(trip_request.interests)}

BUDGET ALLOCATION:
- Accommodation: ${trip_request.budget.get_allocation('accommodation'):.2f}
- Activities: ${trip_request.budget.get_allocation('activities'):.2f}
- Food & Dining: ${trip_request.budget.get_allocation('food'):.2f}
- Transportation: ${trip_request.budget.get_allocation('transport'):.2f}

ACCESSIBILITY NEEDS:
{trip_request.accessibility_needs or 'None specified'}

ADDITIONAL CONSTRAINTS:
{chr(10).join([f'- {k}: {v}' for k, v in trip_request.constraints.items()]) if trip_request.constraints else 'None'}

{weather_section}

REQUIREMENTS FOR THE ITINERARY:
1. Create a day-by-day detailed itinerary
2. Include specific recommendations for:
   - Accommodations (with estimated costs)
   - Restaurants and cafes (with price ranges)
   - Activities and attractions (with duration and cost)
   - Local transportation options
   - Walking routes and public transit
3. Provide realistic time estimates for travel between locations
4. Suggest budget-conscious alternatives
5. Include indoor activities as weather backup options
6. Consider local customs and peak/off-peak hours
7. Suggest accessible alternatives where applicable
8. Provide booking links and reservation tips
9. Include estimated daily costs
10. Format with clear day-by-day breakdown using markdown

Generate a comprehensive, practical, and well-organized itinerary that maximizes the traveler's experience within their budget."""

        return prompt
