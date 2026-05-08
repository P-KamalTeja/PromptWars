"""Google Maps Platform service integration."""
import requests
from typing import Optional, Dict, Any, List

from src.core import Config, get_logger, GoogleServicesError

logger = get_logger(__name__)


class MapsService:
    """Handles Google Maps Platform operations."""

    def __init__(self, config: Config):
        """Initialize Maps service.

        Args:
            config: Application configuration
        """
        self.config = config
        self.api_key = self.config.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"

    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific place.

        Args:
            place_id: Google Place ID

        Returns:
            Place details dictionary or None
        """
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None

        try:
            url = f"{self.base_url}/place/details/json"
            params = {
                "place_id": place_id,
                "key": self.api_key,
                "fields": "name,rating,formatted_address,website,opening_hours,photos,reviews"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "OK":
                return data.get("result")
            
            logger.warning(f"Place details request failed with status: {data.get('status')}")
            return None
        except Exception as e:
            logger.error(f"Maps Place Details failed: {str(e)}")
            return None

    def search_places(self, query: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for places based on a query.

        Args:
            query: Search query (e.g., "restaurants in Paris")
            location: Optional location bias

        Returns:
            List of matching places
        """
        if not self.api_key:
            return []

        try:
            url = f"{self.base_url}/place/textsearch/json"
            params = {
                "query": query,
                "key": self.api_key
            }
            if location:
                params["location"] = location

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "OK":
                return data.get("results", [])
            
            return []
        except Exception as e:
            logger.error(f"Maps Place Search failed: {str(e)}")
            return []

    def get_distance_matrix(self, origins: List[str], destinations: List[str], mode: str = "driving") -> Optional[Dict[str, Any]]:
        """Get distance and travel time between locations.

        Args:
            origins: List of starting points
            destinations: List of destinations
            mode: Travel mode (driving, walking, bicycling, transit)

        Returns:
            Distance matrix data or None
        """
        if not self.api_key:
            return None

        try:
            url = f"{self.base_url}/distancematrix/json"
            params = {
                "origins": "|".join(origins),
                "destinations": "|".join(destinations),
                "mode": mode,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "OK":
                return data
            
            return None
        except Exception as e:
            logger.error(f"Maps Distance Matrix failed: {str(e)}")
            return None

    def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """Get coordinates for an address.

        Args:
            address: Address or city name

        Returns:
            Geocoding results or None
        """
        if not self.api_key:
            return None

        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                "address": address,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "OK" and data.get("results"):
                return data["results"][0]
            
            return None
        except Exception as e:
            logger.error(f"Maps Geocoding failed: {str(e)}")
            return None
