"""Web UI interface using Gradio."""
import gradio as gr
from datetime import datetime, timedelta

from src.core import Config, get_logger
from src.models import TripRequest, TravelerType, TravelPreferences, Budget
from src.api.trip_engine import TripPlanningEngine


logger = get_logger(__name__)


class GradioUI:
    """Gradio web interface for trip planning."""

    def __init__(self, config: Config):
        """Initialize Gradio UI.

        Args:
            config: Application configuration
        """
        self.config = config
        self.engine = TripPlanningEngine(config)
        self.interface = None

    def plan_trip_handler(
        self,
        destination: str,
        budget: float,
        days: int,
        interests: str,
        travelers: int,
        traveler_type: str,
    ) -> str:
        """Handle trip planning request.

        Args:
            destination: Travel destination
            budget: Total budget
            days: Trip duration
            interests: User interests (comma-separated)
            travelers: Number of travelers
            traveler_type: Type of travelers

        Returns:
            Generated itinerary as markdown
        """
        try:
            # Parse inputs
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=int(days))

            interests_list = [
                i.strip() for i in interests.split(",") if i.strip()
            ]

            preferences = [
                TravelPreferences.CULTURAL,
                TravelPreferences.ADVENTURE,
            ]

            budget_obj = Budget(total=float(budget))

            # Create trip request
            trip_request = TripRequest(
                destination=destination,
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.min.time()),
                travelers=int(travelers),
                traveler_type=TravelerType(traveler_type),
                budget=budget_obj,
                preferences=preferences,
                interests=interests_list,
            )

            # Plan trip
            itinerary = self.engine.plan_trip(trip_request)

            # Format response
            accommodation_budget = itinerary.trip_request.budget.get_allocation(
                "accommodation"
            )

            response = f"""
# ✈️ Your Travel Itinerary for {destination}

**Trip ID:** `{itinerary.trip_id}`
**Duration:** {itinerary.trip_request.duration_days} days
**Budget:** ${itinerary.total_cost:,.2f}
**Travelers:** {travelers}
**Confidence Score:** {itinerary.confidence_score * 100:.1f}%

---

## Trip Overview
- **Destination:** {destination}
- **Start Date:** {itinerary.trip_request.start_date.strftime('%Y-%m-%d')}
- **End Date:** {itinerary.trip_request.end_date.strftime('%Y-%m-%d')}
- **Traveler Type:** {traveler_type}
- **Interests:** {', '.join(interests_list)}

---

## Daily Schedule

{self._format_daily_itineraries(itinerary)}

---

## Budget Breakdown
- **Accommodation:** ${accommodation_budget:,.2f}
- **Activities:** ${itinerary.trip_request.budget.get_allocation('activities'):,.2f}
- **Food & Dining:** ${itinerary.trip_request.budget.get_allocation('food'):,.2f}
- **Transportation:** ${itinerary.trip_request.budget.get_allocation('transport'):,.2f}

---

## Tips
✓ Book accommodations in advance for better rates
✓ Check weather forecasts regularly
✓ Consider purchasing travel insurance
✓ Keep a copy of important documents
✓ Download offline maps for areas with limited connectivity
"""

            logger.info(f"Trip planned successfully: {itinerary.trip_id}")
            return response

        except Exception as e:
            logger.error(f"Trip planning error: {str(e)}")
            return (
                f"❌ Error planning trip: {str(e)}\n\n"
                "Please check your inputs and try again."
            )

    def update_trip_handler(self, trip_id: str, update_request: str) -> str:
        """Handle trip update request.

        Args:
            trip_id: Trip identifier
            update_request: Update request description

        Returns:
            Updated itinerary as markdown
        """
        try:
            updated_trip = self.engine.update_trip(trip_id, update_request)

            if not updated_trip:
                return (
                    f"❌ Trip '{trip_id}' not found.\n\n"
                    "Please ensure the trip ID is correct."
                )

            return f"""
# ✈️ Updated Itinerary

**Trip ID:** `{updated_trip.trip_id}`
**Last Updated:** {updated_trip.updated_at.strftime('%Y-%m-%d %H:%M:%S')}

Your itinerary has been successfully updated based on your request:
*{update_request}*

---

{self._format_daily_itineraries(updated_trip)}
"""

        except Exception as e:
            logger.error(f"Trip update error: {str(e)}")
            return f"❌ Error updating trip: {str(e)}\n\nPlease try again."

    @staticmethod
    def _format_daily_itineraries(itinerary) -> str:
        """Format daily itineraries for display.

        Args:
            itinerary: Itinerary object

        Returns:
            Formatted markdown
        """
        days_md = []

        for day in itinerary.daily_itineraries:
            day_md = f"""### Day {day.day_number} - {day.date.strftime('%A, %B %d')}

**Accommodation:** {day.accommodation or 'TBD'}
**Daily Budget:** ${day.get_total_cost():,.2f}"""

            if day.weather:
                day_md += f"""
**Weather:** {day.weather.condition} ({day.weather.temperature}°C)
"""

            days_md.append(day_md)

        return "\n\n".join(days_md)

    def create_interface(self):
        """Create and return Gradio interface.

        Returns:
            Gradio Interface object
        """
        with gr.Blocks(
            title="AI Travel Planner",
            theme=gr.themes.Soft(),
        ) as demo:
            gr.Markdown(
                """
# 🌍 AI-Powered Travel Planning Platform

Create personalized travel itineraries in seconds using AI-powered recommendations.
Customize based on your budget, interests, and preferences.
"""
            )

            with gr.Tabs():
                # Trip Planning Tab
                with gr.Tab("Plan Your Trip", id="plan"):
                    with gr.Row():
                        with gr.Column():
                            destination = gr.Textbox(
                                label="🏖️ Destination",
                                placeholder="e.g., Paris, Tokyo, New York",
                                info="Where do you want to travel?",
                            )
                            budget = gr.Number(
                                label="💰 Total Budget (USD)",
                                value=2000,
                                minimum=100,
                                maximum=1000000,
                                info="Total budget for the trip",
                            )
                            days = gr.Slider(
                                minimum=1,
                                maximum=30,
                                value=5,
                                step=1,
                                label="📅 Trip Duration (Days)",
                                info="How many days?",
                            )

                        with gr.Column():
                            interests = gr.Textbox(
                                label="⭐ Interests",
                                placeholder="Museums, Hiking, Food, History, Shopping",
                                info="Enter interests separated by commas",
                            )
                            travelers = gr.Number(
                                label="👥 Number of Travelers",
                                value=1,
                                minimum=1,
                                maximum=100,
                                info="How many people?",
                            )
                            traveler_type = gr.Dropdown(
                                choices=[
                                    "solo",
                                    "couple",
                                    "family",
                                    "group",
                                ],
                                value="solo",
                                label="👨‍👩‍👧 Traveler Type",
                                info="What type of travelers?",
                            )

                    plan_btn = gr.Button(
                        "🚀 Generate Itinerary",
                        variant="primary",
                        size="lg",
                    )

                    itinerary_output = gr.Markdown(
                        label="Your Itinerary",
                        value="Your itinerary will appear here...",
                    )

                    plan_btn.click(
                        self.plan_trip_handler,
                        inputs=[
                            destination,
                            budget,
                            days,
                            interests,
                            travelers,
                            traveler_type,
                        ],
                        outputs=itinerary_output,
                    )

                # Update Trip Tab
                with gr.Tab("Update Itinerary", id="update"):
                    gr.Markdown(
                        "Have a trip planned already? Update it with your preferences!"
                    )

                    with gr.Row():
                        trip_id = gr.Textbox(
                            label="Trip ID",
                            placeholder="Paste your trip ID here",
                            info="You received this when you planned your trip",
                        )

                    update_request = gr.Textbox(
                        label="What would you like to change?",
                        placeholder=(
                            "e.g., Add more museums, reduce budget, "
                            "add family-friendly activities"
                        ),
                        lines=4,
                        info="Describe your changes or preferences",
                    )

                    update_btn = gr.Button(
                        "✏️ Update Itinerary",
                        variant="primary",
                    )

                    update_output = gr.Markdown(
                        label="Updated Itinerary",
                        value="Updated itinerary will appear here...",
                    )

                    update_btn.click(
                        self.update_trip_handler,
                        inputs=[trip_id, update_request],
                        outputs=update_output,
                    )

                # Info Tab
                with gr.Tab("About", id="about"):
                    gr.Markdown(
                        """
## About This Platform

🌟 **Features:**
- ✅ AI-powered itinerary generation using Google Gemini
- ✅ Real-time weather integration
- ✅ Budget-conscious recommendations
- ✅ Accessibility-friendly planning
- ✅ Personalized suggestions based on your interests
- ✅ Easy updates and modifications

## How It Works

1. **Enter Your Details:** Tell us your destination, budget, and preferences
2. **AI Magic:** Our AI generates a personalized itinerary
3. **Get Your Trip ID:** Save your trip for future updates
4. **Update Anytime:** Modify your itinerary as needed

## Pricing
- 🎉 Completely free to use
- 💡 Powered by Google AI services
- 🌐 Cloud-based and always available

## Contact & Support
For issues or suggestions, please contact our support team.
"""
                    )

        return demo

    def launch(
        self,
        share: bool = False,
        server_name: str = None,
        server_port: int = None,
    ):
        """Launch the Gradio interface.

        Args:
            share: Whether to share the interface
            server_name: Server hostname
            server_port: Server port
        """
        server_name = server_name or self.config.HOST
        server_port = server_port or self.config.PORT

        self.interface = self.create_interface()

        logger.info(f"Launching Gradio UI on {server_name}:{server_port}")

        self.interface.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            show_error=True,
            show_api=True,
        )
