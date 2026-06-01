"""
Orion SDK - Provider Registry
"""

from .base import Provider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .google import GoogleProvider
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider

# ── Built-in provider registry ──────────────────────────────────────

PROVIDER_REGISTRY: dict[str, type[Provider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "google": GoogleProvider,
    "openrouter": OpenRouterProvider,
    "ollama": OllamaProvider,
}

# ── Aliases (user-friendly names) ───────────────────────────────────

PROVIDER_ALIASES: dict[str, str] = {
    "claude": "anthropic",
    "anthropic-claude": "anthropic",
    "gpt": "openai",
    "openai-gpt": "openai",
    "gemini": "google",
    "google-gemini": "google",
    "openai-compatible": "openai",  # Custom OpenAI-compatible endpoints
    "local": "ollama",
}


def get_provider_class(name: str) -> type[Provider]:
    """Resolve a provider name (or alias) to its class.

    Args:
        name: Provider name or alias.

    Returns:
        The :class:`Provider` subclass.

    Raises:
        ValueError: If the name is unknown.
    """
    name_lower = name.lower().strip()
    name_lower = PROVIDER_ALIASES.get(name_lower, name_lower)

    if name_lower not in PROVIDER_REGISTRY:
        available = sorted(set(PROVIDER_REGISTRY) | set(PROVIDER_ALIASES))
        raise ValueError(
            f"Unknown provider '{name}'. Available: {available}"
        )

    return PROVIDER_REGISTRY[name_lower]


def register_provider(name: str, provider_class: type[Provider]):
    """Register a custom provider class.

    Args:
        name: Short name to register under.
        provider_class: A :class:`Provider` subclass.

    Raises:
        TypeError: If *provider_class* is not a :class:`Provider` subclass.
    """
    if not issubclass(provider_class, Provider):
        raise TypeError(f"{provider_class} must be a subclass of Provider")
    PROVIDER_REGISTRY[name.lower()] = provider_class


def list_providers() -> list[str]:
    """List all registered provider names."""
    return list(PROVIDER_REGISTRY.keys())


__all__ = [
    "Provider",
    "AnthropicProvider",
    "OpenAIProvider",
    "GoogleProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "PROVIDER_REGISTRY",
    "PROVIDER_ALIASES",
    "get_provider_class",
    "register_provider",
    "list_providers",
]
