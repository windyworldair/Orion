"""
Orion SDK - Token Counting Utilities
Supports tiktoken (OpenAI) and a character-based estimator for other providers.
"""

import re
from typing import Optional

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


def count_tokens(text: str, model: str = "default") -> int:
    """Count tokens for a given text string.

    Uses *tiktoken* if available (for OpenAI-compatible models).
    Falls back to a character-based estimator (~4 chars per token).

    Args:
        text: The text to count tokens for.
        model: Model name for tokenizer selection.

    Returns:
        Estimated token count.
    """
    if not text:
        return 0

    if HAS_TIKTOKEN:
        try:
            encoding_name = _get_encoding_name(model)
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))
        except Exception:
            pass

    # Fallback: ~4 chars per token (English average)
    return len(text) // 4


def _get_encoding_name(model: str) -> str:
    """Map model names to tiktoken encoding names."""
    model_lower = model.lower()

    if "o1" in model_lower or "o3" in model_lower:
        return "o200k_base"
    if "gpt-4o" in model_lower:
        return "o200k_base"
    if "gpt-4" in model_lower:
        return "cl100k_base"
    if "gpt-3.5" in model_lower:
        return "cl100k_base"
    if "claude" in model_lower:
        return "cl100k_base"
    if "gemini" in model_lower:
        return "cl100k_base"

    return "cl100k_base"


def count_messages_tokens(messages: list, model: str = "default") -> int:
    """Count tokens for a list of chat messages.

    Adds overhead for message formatting (role, separators).

    Args:
        messages: List of ``Message`` objects or ``{"role": ..., "content": ...}`` dicts.
        model: Model name for tokenizer selection.

    Returns:
        Estimated total token count.
    """
    total = 0
    for msg in messages:
        # Support both Message objects and plain dicts
        if hasattr(msg, "content"):
            content = msg.content
        elif isinstance(msg, dict):
            content = msg.get("content", "")
        else:
            content = str(msg)

        if isinstance(content, list):
            # Multimodal content (text + images)
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        total += count_tokens(part.get("text", ""), model)
                    elif part.get("type") == "image_url":
                        total += 85  # Low-res default
        else:
            total += count_tokens(str(content), model)

        # Role + formatting overhead (~4 tokens per message)
        total += 4

    # Final assistant response overhead
    total += 3
    return total


# ── Context window limits (input tokens) for known models ────────────

CONTEXT_LIMITS: dict[str, int] = {
    # OpenAI
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4": 8192,
    "gpt-3.5-turbo": 16385,
    "o1": 200000,
    "o1-mini": 128000,
    "o1-preview": 128000,
    "o3-mini": 200000,
    "o3": 200000,
    # Anthropic
    "claude-opus-4-20250514": 200000,
    "claude-sonnet-4-20250514": 200000,
    "claude-3-5-sonnet-20241022": 200000,
    "claude-3-5-haiku-20241022": 200000,
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    # Google
    "gemini-2.5-pro": 1048576,
    "gemini-2.5-flash": 1048576,
    "gemini-2.0-flash": 1048576,
    "gemini-1.5-pro": 2097152,
    "gemini-1.5-flash": 1048576,
    # xAI
    "grok-3": 131072,
    "grok-3-mini": 131072,
    # Meta (via Ollama / OpenRouter)
    "llama-3.1-405b": 131072,
    "llama-3.1-70b": 131072,
    "llama-3.1-8b": 131072,
    "llama-3-70b": 8192,
    "llama-3-8b": 8192,
}


def get_context_limit(model: str) -> Optional[int]:
    """Get the context window limit (input tokens) for a model.

    Performs exact and partial (fuzzy) matching so names like
    ``"claude-3.5-sonnet"`` resolve correctly.

    Args:
        model: Model name (case-insensitive, partial matching supported).

    Returns:
        Context limit in tokens, or ``None`` if unknown.
    """
    model_lower = model.lower().strip()

    # Exact match
    if model_lower in CONTEXT_LIMITS:
        return CONTEXT_LIMITS[model_lower]

    # Partial match (e.g. "claude-3.5-sonnet" → "claude-3-5-sonnet-20241022")
    for key, limit in CONTEXT_LIMITS.items():
        if model_lower in key or key in model_lower:
            return limit

    return None


def estimate_output_tokens(model: str) -> int:
    """Estimate max output tokens for a model.

    Args:
        model: Model name.

    Returns:
        Estimated max output tokens.
    """
    model_lower = model.lower()

    if "o1" in model_lower or "o3" in model_lower:
        return 100000
    if "claude" in model_lower:
        return 8192
    if "gemini" in model_lower:
        return 8192
    if "gpt-4o" in model_lower:
        return 16384
    if "gpt-4" in model_lower:
        return 4096
    if "gpt-3.5" in model_lower:
        return 4096
    if "llama" in model_lower:
        return 4096
    if "grok" in model_lower:
        return 8192

    return 4096
