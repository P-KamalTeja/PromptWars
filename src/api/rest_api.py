"""REST API endpoints."""
from typing import Dict, Any
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps

from src.core import Config, get_logger, APIError, ValidationError
from src.models import TripRequest, TravelerType, TravelPreferences, Budget
from src.api.trip_engine import TripPlanningEngine


logger = get_logger(__name__)


class TravelAPI:
    """REST API for travel planning."""

    def __init__(self, config: Config):
        """Initialize API.

        Args:
            config: Application configuration
        """
        self.config = config
        self.engine = TripPlanningEngine(config)
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes."""
        # Health check
        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify({"status": "healthy", "version": self.config.APP_VERSION})

        # Trip planning
        @self.app.route("/api/v1/trips/plan", methods=["POST"])
        @self._rate_limit
        def plan_trip():
            """Plan a new trip."""
            try:
                data = request.get_json()
                if not data:
                    raise ValidationError("Request body is required")

                # Parse request
                trip_request = self._parse_trip_request(data)

                # Plan trip
                itinerary = self.engine.plan_trip(trip_request)

                return jsonify(itinerary.to_dict()), 201

            except ValidationError as e:
                return (
                    jsonify(
                        {
                            "error": e.message,
                            "error_code": e.error_code,
                            "field": e.field,
                        }
                    ),
                    e.status_code,
                )
            except APIError as e:
                return (
                    jsonify({"error": e.message, "error_code": e.error_code}),
                    e.status_code,
                )
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        # Get trip
        @self.app.route("/api/v1/trips/<trip_id>", methods=["GET"])
        def get_trip(trip_id: str):
            """Retrieve a planned trip."""
            try:
                trip = self.engine.get_trip(trip_id)
                if not trip:
                    return jsonify({"error": "Trip not found"}), 404

                return jsonify(trip.to_dict()), 200

            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        # Update trip
        @self.app.route("/api/v1/trips/<trip_id>/update", methods=["POST"])
        @self._rate_limit
        def update_trip(trip_id: str):
            """Update an existing trip."""
            try:
                data = request.get_json()
                if not data or "update_request" not in data:
                    raise ValidationError("update_request is required")

                updated_trip = self.engine.update_trip(
                    trip_id, data["update_request"]
                )

                if not updated_trip:
                    return jsonify({"error": "Trip not found"}), 404

                return jsonify(updated_trip.to_dict()), 200

            except ValidationError as e:
                return (
                    jsonify(
                        {
                            "error": e.message,
                            "error_code": e.error_code,
                            "field": e.field,
                        }
                    ),
                    e.status_code,
                )
            except APIError as e:
                return (
                    jsonify({"error": e.message, "error_code": e.error_code}),
                    e.status_code,
                )
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

    def _parse_trip_request(self, data: Dict[str, Any]) -> TripRequest:
        """Parse trip request from JSON.

        Args:
            data: Request data

        Returns:
            TripRequest object

        Raises:
            ValidationError: If parsing fails
        """
        required_fields = [
            "destination",
            "start_date",
            "end_date",
            "budget",
            "travelers",
            "preferences",
        ]

        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        try:
            start_date = datetime.fromisoformat(data["start_date"])
            end_date = datetime.fromisoformat(data["end_date"])
        except ValueError:
            raise ValidationError("Invalid date format. Use ISO format: YYYY-MM-DD")

        traveler_type = TravelerType(data.get("traveler_type", "solo"))
        preferences = [TravelPreferences(p) for p in data.get("preferences", [])]

        budget = Budget(
            total=float(data["budget"]),
            currency=data.get("currency", "USD"),
        )

        return TripRequest(
            destination=data["destination"],
            start_date=start_date,
            end_date=end_date,
            travelers=int(data["travelers"]),
            traveler_type=traveler_type,
            budget=budget,
            preferences=preferences,
            interests=data.get("interests", []),
            constraints=data.get("constraints", {}),
            accessibility_needs=data.get("accessibility_needs"),
        )

    def _rate_limit(self, f):
        """Rate limiting decorator.

        Args:
            f: Function to decorate

        Returns:
            Decorated function
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simplified rate limiting - in production would use Redis/cache
            # Rate limit logic would go here
            return f(*args, **kwargs)

        return decorated_function

    def run(self, host: str = None, port: int = None, debug: bool = None):
        """Run the API server.

        Args:
            host: Server host
            port: Server port
            debug: Debug mode
        """
        host = host or self.config.HOST
        port = port or self.config.PORT
        debug = debug if debug is not None else self.config.DEBUG

        logger.info(f"Starting API server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
