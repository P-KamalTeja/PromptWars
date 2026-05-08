"""Input validation module."""
from typing import List
from datetime import datetime
from src.core import ValidationError
from src.models import TripRequest


class InputValidator:
    """Validates all user inputs."""

    @staticmethod
    def validate_destination(destination: str) -> None:
        """Validate destination input.

        Args:
            destination: Destination name

        Raises:
            ValidationError: If destination is invalid
        """
        if not destination or not isinstance(destination, str):
            raise ValidationError(
                "Destination must be a non-empty string",
                field="destination",
            )

        if len(destination) < 2:
            raise ValidationError(
                "Destination must be at least 2 characters",
                field="destination",
            )

        if len(destination) > 100:
            raise ValidationError(
                "Destination must be at most 100 characters",
                field="destination",
            )

        # Check for valid characters (alphanumeric, spaces, hyphens, commas)
        if not all(c.isalnum() or c in " -," for c in destination):
            raise ValidationError(
                "Destination contains invalid characters",
                field="destination",
            )

    @staticmethod
    def validate_budget(budget: float) -> None:
        """Validate budget input.

        Args:
            budget: Budget amount

        Raises:
            ValidationError: If budget is invalid
        """
        if not isinstance(budget, (int, float)):
            raise ValidationError("Budget must be a number", field="budget")

        if budget < 100:
            raise ValidationError("Budget must be at least $100", field="budget")

        if budget > 1000000:
            raise ValidationError("Budget must be at most $1,000,000", field="budget")

    @staticmethod
    def validate_duration(start_date: datetime, end_date: datetime) -> None:
        """Validate trip duration.

        Args:
            start_date: Trip start date
            end_date: Trip end date

        Raises:
            ValidationError: If dates are invalid
        """
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValidationError("Dates must be datetime objects")

        if start_date >= end_date:
            raise ValidationError("End date must be after start date")

        duration = (end_date - start_date).days
        if duration < 1:
            raise ValidationError("Trip must be at least 1 day", field="duration")

        if duration > 365:
            raise ValidationError("Trip must be at most 365 days", field="duration")

    @staticmethod
    def validate_travelers(travelers: int) -> None:
        """Validate number of travelers.

        Args:
            travelers: Number of travelers

        Raises:
            ValidationError: If travelers count is invalid
        """
        if not isinstance(travelers, int):
            raise ValidationError(
                "Number of travelers must be an integer",
                field="travelers",
            )

        if travelers < 1:
            raise ValidationError("Must have at least 1 traveler", field="travelers")

        if travelers > 100:
            raise ValidationError(
                "Cannot plan for more than 100 travelers",
                field="travelers",
            )

    @staticmethod
    def validate_interests(interests: List[str]) -> None:
        """Validate interests list.

        Args:
            interests: List of interests

        Raises:
            ValidationError: If interests are invalid
        """
        if not isinstance(interests, list):
            raise ValidationError("Interests must be a list", field="interests")

        if len(interests) > 20:
            raise ValidationError("Maximum 20 interests allowed", field="interests")

        for interest in interests:
            if not isinstance(interest, str) or len(interest) > 50:
                raise ValidationError(
                    "Each interest must be a string with max 50 characters",
                    field="interests",
                )

    @staticmethod
    def validate_trip_request(request: TripRequest) -> None:
        """Validate complete trip request.

        Args:
            request: Trip request object

        Raises:
            ValidationError: If request is invalid
        """
        InputValidator.validate_destination(request.destination)
        InputValidator.validate_budget(request.budget.total)
        InputValidator.validate_duration(request.start_date, request.end_date)
        InputValidator.validate_travelers(request.travelers)
        InputValidator.validate_interests(request.interests)
