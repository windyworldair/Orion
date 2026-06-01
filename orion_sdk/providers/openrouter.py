"""
Orion SDK - OpenRouter Provider
Routes requests through OpenRouter's unified API (100+ models).
"""

from typing import Iterator

from .openai import OpenAIProvider
from .base import ProviderConfig


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter API provider.

    Routes to 100+ models (Anthropic, OpenAI, Google, xAI, Meta, Mistral,
    DeepSeek, Qwen, Perplexity, and more) through a single OpenAI-compatible
    API.  Inherits the full :class:`OpenAIProvider` implementation.
    """

    NAME = "openrouter"
    MODELS = {
        # Anthropic
        "anthropic/claude-opus-4": {"context": 200000, "output": 32000},
        "anthropic/claude-sonnet-4": {"context": 200000, "output": 16000},
        "anthropic/claude-3.5-sonnet": {"context": 200000, "output": 8192},
        "anthropic/claude-3.5-haiku": {"context": 200000, "output": 8192},
        # OpenAI
        "openai/gpt-4o": {"context": 128000, "output": 16384},
        "openai/gpt-4o-mini": {"context": 128000, "output": 16384},
        "openai/o1": {"context": 200000, "output": 100000},
        "openai/o1-mini": {"context": 128000, "output": 65536},
        "openai/o3-mini": {"context": 200000, "output": 100000},
        # Google
        "google/gemini-2.5-pro-preview": {"context": 1048576, "output": 65536},
        "google/gemini-2.5-flash-preview": {"context": 1048576, "output": 65536},
        "google/gemini-2.0-flash-001": {"context": 1048576, "output": 8192},
        # xAI
        "x-ai/grok-3": {"context": 131072, "output": 8192},
        "x-ai/grok-3-mini": {"context": 131072, "output": 8192},
        # Meta
        "meta-llama/llama-3.1-405b-instruct": {"context": 131072, "output": 4096},
        "meta-llama/llama-3.1-70b-instruct": {"context": 131072, "output": 4096},
        "meta-llama/llama-3.1-8b-instruct": {"context": 131072, "output": 4096},
        # Mistral
        "mistralai/mistral-large": {"context": 131072, "output": 4096},
        # DeepSeek
        "deepseek/deepseek-chat": {"context": 131072, "output": 8192},
        "deepseek/deepseek-r1": {"context": 131072, "output": 8192},
        # Qwen
        "qwen/qwen-2.5-72b-instruct": {"context": 131072, "output": 4096},
        # Perplexity
        "perplexity/sonar": {"context": 200000, "output": 8192},
    }

    def __init__(self, config: ProviderConfig):
        # Point to OpenRouter's API unless a custom base_url was given
        if not config.base_url:
            config = ProviderConfig(
                api_key=config.api_key,
                base_url="https://openrouter.ai/api/v1",
                organization=config.organization,
                timeout=config.timeout,
                max_retries=config.max_retries,
                verify_ssl=config.verify_ssl,
            )
        super().__init__(config)

    @property
    def default_model(self) -> str:
        """Default model for OpenRouter."""
        return "anthropic/claude-sonnet-4"

    @property
    def requires_api_key(self) -> bool:
        return True
