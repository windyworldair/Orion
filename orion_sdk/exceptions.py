"""
Orion SDK - Custom Exceptions
"""

__all__ = [
    "OrionError",
    "ProviderError",
    "ProviderNotFoundError",
    "ModelNotFoundError",
    "AuthenticationError",
    "RateLimitError",
    "ContextOverflowError",
    "AllProvidersFailedError",
    "TimeoutError",
    "InvalidConfigError",
]


class OrionError(Exception):
    """Base exception for all Orion SDK errors."""
    pass


class ProviderError(OrionError):
    """Error originating from a specific provider."""

    def __init__(self, provider: str, message: str, status_code: int = None):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class ProviderNotFoundError(OrionError):
    """Requested provider is not registered."""

    def __init__(self, provider: str):
        self.provider = provider
        super().__init__(
            f"Provider '{provider}' not found. "
            "Check OrionClient.list_providers() for available providers."
        )


class ModelNotFoundError(OrionError):
    """Requested model is not available for the provider."""

    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        super().__init__(
            f"Model '{model}' not available on provider '{provider}'"
        )


class AuthenticationError(ProviderError):
    """Invalid or missing API key."""

    def __init__(self, provider: str):
        super().__init__(
            provider,
            f"Authentication failed. Check your {provider} API key.",
            401,
        )


class RateLimitError(ProviderError):
    """Rate limit hit on a provider."""

    def __init__(self, provider: str, retry_after: float = None):
        self.retry_after = retry_after
        msg = "Rate limit exceeded."
        if retry_after:
            msg += f" Retry after {retry_after}s"
        super().__init__(provider, msg, 429)


class ContextOverflowError(OrionError):
    """Input exceeds model context window."""

    def __init__(self, tokens: int, limit: int, model: str):
        self.tokens = tokens
        self.limit = limit
        self.model = model
        super().__init__(
            f"Input ({tokens} tokens) exceeds {model} context window "
            f"({limit} tokens)"
        )


class AllProvidersFailedError(OrionError):
    """All providers in the fallback chain failed."""

    def __init__(self, errors: list):
        self.errors = errors
        details = "\n".join(f"  - {e}" for e in errors)
        super().__init__(f"All providers failed:\n{details}")


class TimeoutError(ProviderError):
    """Request timed out."""

    def __init__(self, provider: str, timeout: float):
        super().__init__(provider, f"Request timed out after {timeout}s", None)


class InvalidConfigError(OrionError):
    """Invalid SDK configuration."""
    pass
