"""Custom exception classes."""


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
    ):
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Machine-readable error code
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class ValidationError(APIError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None):
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
        """
        self.field = field
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")


class TravelPlanningError(APIError):
    """Raised when trip planning fails."""

    def __init__(self, message: str):
        """Initialize travel planning error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=500, error_code="PLANNING_ERROR")


class GoogleServicesError(APIError):
    """Raised when Google Services integration fails."""

    def __init__(self, message: str, service: str = None):
        """Initialize Google Services error.

        Args:
            message: Error message
            service: Service that failed (Gemini, Maps, Calendar, etc.)
        """
        self.service = service
        super().__init__(
            message, status_code=502, error_code="GOOGLE_SERVICES_ERROR"
        )


class NotFoundError(APIError):
    """Raised when resource is not found."""

    def __init__(self, message: str, resource: str = None):
        """Initialize not found error.

        Args:
            message: Error message
            resource: Resource type that was not found
        """
        self.resource = resource
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int = 60):
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_EXCEEDED")
