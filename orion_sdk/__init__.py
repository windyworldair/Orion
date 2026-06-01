"""
Orion SDK - The Model-Agnostic AI SDK
======================================

One interface, every LLM.  Built by Zalcus.

Quick start::

    from orion_sdk import create_client

    client = create_client("openai", api_key="sk-...")
    response = client.complete("Hello, world!")
    print(response.content)
"""

__version__ = "1.0.0"
__author__ = "Zalcus"

# ── Client ───────────────────────────────────────────────────────────
from .client import OrionClient, create_client

# ── Base types ───────────────────────────────────────────────────────
from .providers.base import (
    Provider,
    ProviderConfig,
    Message,
    ToolDefinition,
    ToolCall,
    Response,
    StreamChunk,
)

# ── Provider implementations ─────────────────────────────────────────
from .providers import (
    AnthropicProvider,
    OpenAIProvider,
    GoogleProvider,
    OpenRouterProvider,
    OllamaProvider,
    register_provider,
    list_providers,
)

# ── Exceptions ───────────────────────────────────────────────────────
from .exceptions import (
    OrionError,
    ProviderError,
    ProviderNotFoundError,
    ModelNotFoundError,
    AuthenticationError,
    RateLimitError,
    ContextOverflowError,
    AllProvidersFailedError,
    TimeoutError,
    InvalidConfigError,
)

# ── Utilities ────────────────────────────────────────────────────────
from .tokens import (
    count_tokens,
    count_messages_tokens,
    get_context_limit,
    CONTEXT_LIMITS,
)
from .ratelimit import RateLimiter


__all__ = [
    # Client
    "OrionClient",
    "create_client",
    # Base types
    "Provider",
    "ProviderConfig",
    "Message",
    "ToolDefinition",
    "ToolCall",
    "Response",
    "StreamChunk",
    # Providers
    "AnthropicProvider",
    "OpenAIProvider",
    "GoogleProvider",
    "OpenRouterProvider",
    "OllamaProvider",
    "register_provider",
    "list_providers",
    # Exceptions
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
    # Utilities
    "count_tokens",
    "count_messages_tokens",
    "get_context_limit",
    "CONTEXT_LIMITS",
    "RateLimiter",
]
