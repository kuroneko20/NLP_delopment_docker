class ExternalServiceError(RuntimeError):
    """Raised when an external service call fails."""


class ExternalServiceTimeout(ExternalServiceError):
    """Raised when an external service call times out."""
