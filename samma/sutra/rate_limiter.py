"""In-memory sliding window rate limiter with pluggable backend."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Protocol


class RateLimiterBackend(Protocol):
    """Protocol for pluggable rate limiter backends (Redis, etc.)."""

    def record_hit(self, key: str, window_seconds: int) -> int:
        """Record a hit and return the current count within the window."""
        ...

    def get_count(self, key: str, window_seconds: int) -> int:
        """Return current count within the window without recording."""
        ...


class InMemoryBackend:
    """Sliding window rate limiter using in-memory timestamps."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _prune(self, key: str, window_seconds: int) -> None:
        cutoff = time.monotonic() - window_seconds
        self._hits[key] = [t for t in self._hits[key] if t > cutoff]

    def record_hit(self, key: str, window_seconds: int) -> int:
        self._prune(key, window_seconds)
        self._hits[key].append(time.monotonic())
        return len(self._hits[key])

    def get_count(self, key: str, window_seconds: int) -> int:
        self._prune(key, window_seconds)
        return len(self._hits[key])


class RateLimiter:
    """
    Sliding window rate limiter.

    Supports per-IP and per-agent limits with a pluggable backend.
    Default backend is in-memory (suitable for single-worker deployments).
    """

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        backend: RateLimiterBackend | None = None,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._backend = backend or InMemoryBackend()

    def check(self, key: str) -> tuple[bool, int]:
        """
        Record a hit and check if the limit is exceeded.

        Returns:
            (allowed, remaining) — allowed is False if over limit.
        """
        count = self._backend.record_hit(key, self.window_seconds)
        remaining = max(0, self.max_requests - count)
        return count <= self.max_requests, remaining

    def remaining(self, key: str) -> int:
        """Return remaining requests for a key without recording a hit."""
        count = self._backend.get_count(key, self.window_seconds)
        return max(0, self.max_requests - count)
