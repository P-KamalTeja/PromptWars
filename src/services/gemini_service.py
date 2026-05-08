"""Google Services integration module."""
import json
from typing import Any, Dict, List, Optional, Union

import google.generativeai as genai
import vertexai
from vertexai.generative_models import ChatSession, GenerationConfig, GenerativeModel

from src.core import Config, get_logger, GoogleServicesError
from src.models import TripRequest, Weather


logger = get_logger(__name__)


class GeminiService:
    """Handles Gemini AI integrations via both Generative AI SDK and Vertex AI."""

    def __init__(self, config: Config):
        """Initialize Gemini service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.model = None
        self.chat_sessions: Dict[str, Union[genai.ChatSession, ChatSession]] = {}
        self._initialize_client()

    def _initialize_client(self):
        """Initialize appropriate Gemini client based on config."""
        try:
            if self.config.USE_VERTEX_AI and self.config.GOOGLE_CLOUD_PROJECT:
                logger.info(
                    "Initializing Vertex AI in project %s",
                    self.config.GOOGLE_CLOUD_PROJECT,
                )
                vertexai.init(project=self.config.GOOGLE_CLOUD_PROJECT)
                self.model = GenerativeModel("gemini-1.5-flash")
                logger.info("Vertex AI Gemini client initialized successfully")
            else:
                if not self.config.GEMINI_API_KEY:
                    raise GoogleServicesError(
                        "GEMINI_API_KEY is required for Gemini API access",
                        service="Gemini",
                    )
                logger.info("Initializing Google Generative AI SDK")
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                logger.info(
                    "Google Generative AI Gemini client initialized successfully"
                )
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
        session_id: str,
        user_request: str,
        existing_plan: Optional[str] = None
    ) -> str:
        """Update existing itinerary based on user feedback using chat sessions.

        Args:
            session_id: Unique session ID for the conversation
            user_request: User's update request
            existing_plan: Optional initial plan to start the session

        Returns:
            Updated itinerary

        Raises:
            GoogleServicesError: If update fails
        """
        try:
            if session_id not in self.chat_sessions:
                logger.info(f"Creating new chat session: {session_id}")
                self.chat_sessions[session_id] = self.model.start_chat()
                if existing_plan:
                    # Initialize session with the existing plan
                    initial_msg = (
                        "Here is my existing trip plan:\n\n"
                        f"{existing_plan}\n\nPlease help me update it."
                    )
                    self.chat_sessions[session_id].send_message(initial_msg)

            response = self.chat_sessions[session_id].send_message(user_request)
            logger.info(f"Successfully updated itinerary for session {session_id}")
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
        """Get personalized recommendations with structured JSON output.

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
            prompt = f"""Provide detailed recommendations for a trip to {destination}.
Preferences: {', '.join(preferences)}
Budget: ${budget}
Duration: {duration_days} days

Return a JSON object with the following structure:
{{
    "accommodation": [{{ "name": str, "description": str, "estimated_cost": float }}],
    "restaurants": [{{ "name": str, "cuisine": str, "price_range": str }}],
    "attractions": [{{ "name": str, "description": str, "best_time": str }}],
    "transport": [{{ "type": str, "cost_level": str, "pro_tip": str }}],
    "local_tips": [str]
}}
"""
            generation_config = None
            if self.config.USE_VERTEX_AI:
                generation_config = GenerationConfig(
                    response_mime_type="application/json"
                )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )

            content = response.text
            # If not using Vertex AI or if it didn't return pure JSON, try to parse
            try:
                # Basic cleaning if AI wrapped in markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning(
                    "Failed to parse Gemini response as JSON, returning raw text"
                )
                return {"raw_response": content}

        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            raise GoogleServicesError(
                f"Failed to generate recommendations: {str(e)}", service="Gemini"
            )

    @staticmethod
    def _build_itinerary_prompt(
        trip_request: TripRequest, weather: Optional[Weather] = None
    ) -> str:
        """Build detailed prompt for itinerary generation."""
        weather_section = ""
        if weather:
            weather_section = f"""
Current Weather in {trip_request.destination}:
- Temperature: {weather.temperature}°C
- Condition: {weather.condition}
- Humidity: {weather.humidity}%
"""

        prompt = f"""You are an expert AI travel planner creating a detailed,
personalized travel itinerary.

TRIP DETAILS:
Destination: {trip_request.destination}
Duration: {trip_request.duration_days} days
Travelers: {trip_request.travelers} ({trip_request.traveler_type.value})
Total Budget: ${trip_request.budget.total}

PREFERENCES:
{', '.join([p.value for p in trip_request.preferences])}
Interests: {', '.join(trip_request.interests)}

{weather_section}

REQUIREMENTS:
1. Day-by-day breakdown
2. Specific accommodation and restaurant names
3. Estimated costs for each activity
4. Local transportation tips
5. Format nicely in markdown.

Generate a comprehensive and practical itinerary."""

        return prompt
