"""
Orion SDK - Rate Limiter
Token-bucket rate limiter for provider API calls.
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TokenBucket:
    """Thread-safe token bucket rate limiter."""

    rate: float  # tokens per second
    capacity: float  # max burst tokens
    tokens: float = field(init=False)
    last_refill: float = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.monotonic()

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """Acquire tokens.  Blocks until tokens are available or *timeout*.

        Args:
            tokens: Number of tokens to acquire.
            timeout: Max wait time in seconds (``None`` = no wait).

        Returns:
            ``True`` if tokens acquired, ``False`` if timed out.
        """
        with self._lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            if timeout is None or timeout <= 0:
                return False

            needed = tokens - self.tokens
            wait_time = needed / self.rate

            if wait_time > timeout:
                return False

        # Wait outside the lock, then retry
        time.sleep(wait_time)
        return self.acquire(tokens, timeout=0)

    def try_acquire(self, tokens: int = 1) -> bool:
        """Non-blocking acquire.  Returns immediately."""
        return self.acquire(tokens, timeout=0)


class RateLimiter:
    """Multi-provider rate limiter with separate token buckets per provider."""

    def __init__(self):
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def register(self, provider: str, requests_per_minute: float, burst: int = 5):
        """Register rate limits for a provider.

        Args:
            provider: Provider name.
            requests_per_minute: Max requests per minute.
            burst: Max burst size (default 5).
        """
        rate = requests_per_minute / 60.0
        bucket = TokenBucket(rate=rate, capacity=burst)
        with self._lock:
            self._buckets[provider] = bucket

    def acquire(self, provider: str, timeout: Optional[float] = 30.0) -> bool:
        """Acquire a request slot for a provider.

        Args:
            provider: Provider name.
            timeout: Max wait time in seconds.

        Returns:
            ``True`` if a slot was acquired.
        """
        with self._lock:
            bucket = self._buckets.get(provider)

        if bucket is None:
            return True  # No rate limit registered = unlimited

        return bucket.acquire(timeout=timeout)

    def get_stats(self, provider: str) -> dict:
        """Get rate-limiter stats for a provider."""
        with self._lock:
            bucket = self._buckets.get(provider)

        if bucket is None:
            return {"provider": provider, "limited": False}

        with bucket._lock:
            bucket._refill()
            return {
                "provider": provider,
                "limited": True,
                "available_tokens": round(bucket.tokens, 2),
                "capacity": bucket.capacity,
                "rate": round(bucket.rate, 4),
            }
