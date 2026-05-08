"""Modern web interface using Flask and HTML/CSS/JS."""
from flask import Flask, render_template, request, jsonify, send_from_directory

from src.core import Config, get_logger
from src.models import TripRequest, TravelerType, TravelPreferences, Budget
from datetime import datetime, timedelta


logger = get_logger(__name__)


class WebUI:
    """Modern web interface for trip planning."""

    def __init__(self, config: Config):
        """Initialize web UI.

        Args:
            config: Application configuration
        """
        self.config = config
        self._engine = None

        self.app = Flask(
            __name__,
            template_folder="src/ui/templates",
            static_folder="src/ui/static",
        )

        self._setup_routes()

    @property
    def engine(self):
        """Create the trip engine only when an API request needs it."""
        if self._engine is None:
            from src.api.trip_engine import TripPlanningEngine

            self._engine = TripPlanningEngine(self.config)
        return self._engine

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """Serve main page."""
            return render_template("index.html")

        @self.app.route("/static/<path:filename>")
        def serve_static(filename):
            """Serve static files."""
            return send_from_directory(self.app.static_folder, filename)

        @self.app.route("/health")
        def health():
            """Health check endpoint for Cloud Run."""
            return "OK", 200

        @self.app.route("/api/plan", methods=["POST"])
        def plan_trip():
            """API endpoint for trip planning."""
            try:
                data = request.get_json()

                # Validate required fields
                required = ["destination", "budget", "days", "travelers"]
                if not all(field in data for field in required):
                    return jsonify({"error": "Missing required fields"}), 400

                # Parse request
                start_date = datetime.now()
                end_date = start_date + timedelta(days=int(data["days"]))

                interests = [
                    i.strip()
                    for i in data.get("interests", "").split(",")
                    if i.strip()
                ]

                preferences = [
                    TravelPreferences.CULTURAL,
                    TravelPreferences.ADVENTURE,
                ]

                trip_request = TripRequest(
                    destination=data["destination"],
                    start_date=start_date,
                    end_date=end_date,
                    travelers=int(data["travelers"]),
                    traveler_type=TravelerType(
                        data.get("traveler_type", "solo")
                    ),
                    budget=Budget(total=float(data["budget"])),
                    preferences=preferences,
                    interests=interests,
                )

                # Plan trip
                itinerary = self.engine.plan_trip(trip_request)

                return jsonify(
                    {
                        "trip_id": itinerary.trip_id,
                        "destination": itinerary.destination.name,
                        "duration": itinerary.trip_request.duration_days,
                        "total_cost": itinerary.total_cost,
                        "confidence_score": itinerary.confidence_score,
                        "daily_itineraries": len(itinerary.daily_itineraries),
                    }
                ), 201

            except Exception as e:
                logger.error(f"Trip planning error: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/trips/<trip_id>", methods=["GET"])
        def get_trip(trip_id: str):
            """Get trip details."""
            try:
                trip = self.engine.get_trip(trip_id)
                if not trip:
                    return jsonify({"error": "Trip not found"}), 404

                return jsonify(trip.to_dict()), 200

            except Exception as e:
                logger.error(f"Retrieve error: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/trips/<trip_id>/update", methods=["POST"])
        def update_trip(trip_id: str):
            """Update trip."""
            try:
                data = request.get_json()
                if not data or "update_request" not in data:
                    return jsonify({"error": "Missing update_request"}), 400

                updated_trip = self.engine.update_trip(
                    trip_id, data["update_request"]
                )

                if not updated_trip:
                    return jsonify({"error": "Trip not found"}), 404

                return jsonify(updated_trip.to_dict()), 200

            except Exception as e:
                logger.error(f"Update error: {str(e)}")
                return jsonify({"error": str(e)}), 500

    def run(
        self,
        host: str = None,
        port: int = None,
        debug: bool = None,
    ):
        """Run the web server.

        Args:
            host: Server host
            port: Server port
            debug: Debug mode
        """
        host = host or self.config.HOST
        port = port or self.config.PORT
        debug = debug if debug is not None else self.config.DEBUG

        logger.info(f"Starting Web UI on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=debug)
