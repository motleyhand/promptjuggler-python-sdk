from __future__ import annotations


class PromptJugglerError(Exception):
    """Base class for every error the SDK raises. Catch this to handle any SDK failure."""


class ApiError(PromptJugglerError):
    """Raised when the API responds with a non-2xx status."""

    def __init__(self, message: str, status_code: int | None) -> None:
        super().__init__(message)
        self.status_code = status_code


class NetworkError(PromptJugglerError):
    """Raised when the request never reached the API (DNS failure, timeout, offline)."""


class DecodeError(PromptJugglerError):
    """Raised when the API replied with a success status but the body didn't decode into the expected
    model. The request succeeded, so retrying a run starts a second one."""
