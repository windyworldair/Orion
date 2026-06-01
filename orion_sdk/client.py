"""
Orion SDK - Main Client
Unified interface to all model providers with fallback chains, retry logic,
and automatic token management.
"""

import time
from typing import Optional, Iterator

from .providers.base import (
    Provider, ProviderConfig, Response, StreamChunk,
    Message, ToolDefinition,
)
from .providers import get_provider_class, register_provider, list_providers
from .tokens import count_messages_tokens, get_context_limit
from .ratelimit import RateLimiter
from .exceptions import (
    OrionError, ProviderError, ProviderNotFoundError,
    AllProvidersFailedError, ContextOverflowError,
)


class OrionClient:
    """The main Orion SDK client.

    Unified interface to any AI model provider.  Supports fallback chains,
    streaming, tool calling, token counting, and automatic retries.

    Example::

        >>> from orion_sdk import OrionClient
        >>> client = OrionClient()
        >>> client.add_provider("anthropic", api_key="sk-ant-...")
        >>> response = client.complete("Hello, world!")
        >>> print(response.content)
    """

    def __init__(self, config: dict = None):
        """Initialize the Orion client.

        Args:
            config: Optional dict with global settings:

                - ``default_provider`` (*str*)
                - ``default_model`` (*str*)
                - ``timeout`` (*float*) – default 120 s
                - ``max_retries`` (*int*) – default 3
                - ``rate_limits`` (*dict*) – ``{provider: requests_per_minute}``
        """
        config = config or {}
        self._providers: dict[str, Provider] = {}
        self._fallback_chain: list[str] = []
        self._rate_limiter = RateLimiter()
        self._default_provider: str = config.get("default_provider", "")
        self._default_model: str = config.get("default_model", "")
        self._global_timeout: float = config.get("timeout", 120.0)
        self._global_max_retries: int = config.get("max_retries", 3)

        # Set up per-provider rate limits
        rate_limits = config.get("rate_limits", {})
        for provider, rpm in rate_limits.items():
            self._rate_limiter.register(provider, rpm)

    # ── Provider management ──────────────────────────────────────────

    def add_provider(
        self,
        name: str,
        api_key: str = "",
        base_url: str = "",
        organization: str = "",
        timeout: float = None,
        max_retries: int = None,
        set_default: bool = False,
    ) -> Provider:
        """Register a provider with credentials.

        Args:
            name: Provider name (``"anthropic"``, ``"openai"``, ``"google"``,
                  ``"openrouter"``, ``"ollama"``, or a custom alias).
            api_key: API key for the provider.
            base_url: Custom base URL (for self-hosted / OpenAI-compatible endpoints).
            organization: Organization ID (OpenAI only).
            timeout: Request timeout in seconds.
            max_retries: Max retry attempts.
            set_default: Make this the default provider.

        Returns:
            The created :class:`Provider` instance.

        Raises:
            ValueError: If provider name is unknown.
        """
        provider_class = get_provider_class(name)

        config = ProviderConfig(
            api_key=api_key,
            base_url=base_url,
            organization=organization,
            timeout=timeout or self._global_timeout,
            max_retries=max_retries or self._global_max_retries,
        )

        provider = provider_class(config)
        self._providers[name] = provider

        if set_default or not self._default_provider:
            self._default_provider = name

        # Register default rate limit if not already configured
        if name not in self._rate_limiter._buckets:
            self._rate_limiter.register(name, 60)  # 60 req/min default

        return provider

    def remove_provider(self, name: str):
        """Remove a registered provider."""
        self._providers.pop(name, None)
        if self._default_provider == name:
            self._default_provider = next(iter(self._providers), "")

    # ── Fallback chains ──────────────────────────────────────────────

    def set_fallback_chain(self, *providers: str):
        """Set the fallback chain for automatic failover.

        When the primary provider fails, Orion tries the next provider in the
        chain.

        Args:
            *providers: Provider names in priority order.

        Example::

            client.set_fallback_chain("anthropic", "openai", "google")
        """
        for p in providers:
            if p not in self._providers:
                raise ProviderNotFoundError(p)
        self._fallback_chain = list(providers)

    # ── Completion ───────────────────────────────────────────────────

    def complete(
        self,
        prompt: str,
        provider: str = "",
        model: str = "",
        system: str = "",
        messages: list[Message] = None,
        tools: list[ToolDefinition] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_fallback: bool = True,
        **kwargs,
    ) -> Response:
        """Send a completion request.

        Args:
            prompt: The user message (or use *messages* for a full conversation).
            provider: Provider name (uses default if empty).
            model: Model name (uses provider default if empty).
            system: System prompt.
            messages: Full message list (overrides *prompt* + *system*).
            tools: Tool definitions for function calling.
            temperature: Sampling temperature (0.0 – 2.0).
            max_tokens: Max output tokens.
            use_fallback: Whether to try the fallback chain on failure.
            **kwargs: Provider-specific options.

        Returns:
            :class:`Response` with ``content``, ``tool_calls``, ``usage``, etc.
        """
        # Build message list
        if messages is None:
            msgs: list[Message] = []
            if system:
                msgs.append(Message.system(system))
            msgs.append(Message.user(prompt))
        else:
            msgs = messages

        # Determine which providers to try
        if provider:
            providers_to_try = [provider]
        elif self._fallback_chain:
            providers_to_try = self._fallback_chain
        elif self._default_provider:
            providers_to_try = [self._default_provider]
        else:
            raise OrionError("No provider configured. Call add_provider() first.")

        # Validate context window
        if model:
            limit = get_context_limit(model)
            if limit:
                tokens = count_messages_tokens(msgs, model)
                if tokens > limit:
                    raise ContextOverflowError(tokens, limit, model)

        errors: list[str] = []
        for prov_name in providers_to_try:
            prov = self._providers.get(prov_name)
            if not prov:
                errors.append(f"Provider '{prov_name}' not registered")
                continue

            # Rate limit check
            if not self._rate_limiter.acquire(prov_name, timeout=5.0):
                errors.append(f"Rate limited on '{prov_name}'")
                continue

            # Determine model
            effective_model = model or self._default_model or prov.default_model

            try:
                response = prov.complete(
                    messages=msgs,
                    model=effective_model,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                return response
            except Exception as e:
                errors.append(f"[{prov_name}] {e}")
                if not use_fallback or len(providers_to_try) == 1:
                    raise

        raise AllProvidersFailedError(errors)

    # ── Streaming ────────────────────────────────────────────────────

    def stream(
        self,
        prompt: str,
        provider: str = "",
        model: str = "",
        system: str = "",
        messages: list[Message] = None,
        tools: list[ToolDefinition] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> Iterator[StreamChunk]:
        """Stream a completion response.

        Same arguments as :meth:`complete`, but returns an iterator of
        :class:`StreamChunk` objects.
        """
        if messages is None:
            msgs: list[Message] = []
            if system:
                msgs.append(Message.system(system))
            msgs.append(Message.user(prompt))
        else:
            msgs = messages

        prov_name = provider or self._default_provider
        if not prov_name:
            raise OrionError("No provider configured.")
        if prov_name not in self._providers:
            raise ProviderNotFoundError(prov_name)

        prov = self._providers[prov_name]
        effective_model = model or self._default_model or prov.default_model

        return prov.stream(
            messages=msgs,
            model=effective_model,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    # ── Token utilities ──────────────────────────────────────────────

    def count_tokens(self, text: str, model: str = "") -> int:
        """Count tokens for *text*."""
        from .tokens import count_tokens
        return count_tokens(text, model)

    def count_messages_tokens(self, messages: list[Message], model: str = "") -> int:
        """Count tokens for a message list."""
        return count_messages_tokens(messages, model)

    def get_context_limit(self, model: str) -> Optional[int]:
        """Get context window limit for *model*."""
        return get_context_limit(model)

    # ── Introspection ────────────────────────────────────────────────

    def list_providers(self) -> list[str]:
        """List registered provider names."""
        return list(self._providers.keys())

    def list_models(self, provider: str = "") -> list[dict]:
        """List available models for a provider (or all)."""
        if provider:
            prov = self._providers.get(provider)
            if not prov:
                raise ProviderNotFoundError(provider)
            return prov.list_models()

        models: list[dict] = []
        for prov in self._providers.values():
            models.extend(prov.list_models())
        return models

    def register_custom_provider(self, name: str, provider_class: type[Provider]):
        """Register a custom provider class."""
        register_provider(name, provider_class)

    # ── Properties ───────────────────────────────────────────────────

    @property
    def default_provider(self) -> str:
        """Name of the current default provider."""
        return self._default_provider

    @default_provider.setter
    def default_provider(self, name: str):
        if name not in self._providers:
            raise ProviderNotFoundError(name)
        self._default_provider = name

    def __repr__(self) -> str:
        providers = list(self._providers.keys())
        default = self._default_provider
        return f"OrionClient(providers={providers}, default={default})"


# ── Convenience factory ──────────────────────────────────────────────

def create_client(
    provider: str = "openai",
    api_key: str = "",
    model: str = "",
    **kwargs,
) -> OrionClient:
    """Quick-create an :class:`OrionClient` with one provider.

    Args:
        provider: Provider name.
        api_key: API key.
        model: Default model.
        **kwargs: Additional args passed to :class:`OrionClient`.

    Returns:
        A configured :class:`OrionClient` instance.

    Example::

        >>> client = create_client("openai", api_key="sk-...")
        >>> response = client.complete("Hello!")
    """
    client = OrionClient(config=kwargs)
    client.add_provider(provider, api_key=api_key, set_default=True)
    if model:
        client._default_model = model
    return client
