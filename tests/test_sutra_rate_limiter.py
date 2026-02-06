"""Unit tests for the SUTRA sliding window rate limiter."""

import pytest
from samma.sutra.rate_limiter import RateLimiter, InMemoryBackend


class TestInMemoryBackend:
    def test_record_hit_increments(self):
        backend = InMemoryBackend()
        count = backend.record_hit("key1", 60)
        assert count == 1
        count = backend.record_hit("key1", 60)
        assert count == 2

    def test_get_count_without_recording(self):
        backend = InMemoryBackend()
        backend.record_hit("key1", 60)
        backend.record_hit("key1", 60)
        assert backend.get_count("key1", 60) == 2

    def test_different_keys_are_independent(self):
        backend = InMemoryBackend()
        backend.record_hit("key1", 60)
        backend.record_hit("key2", 60)
        assert backend.get_count("key1", 60) == 1
        assert backend.get_count("key2", 60) == 1


class TestRateLimiter:
    def test_under_limit_allowed(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        allowed, remaining = limiter.check("client1")
        assert allowed is True
        assert remaining == 2

    def test_at_limit_still_allowed(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        limiter.check("client1")
        limiter.check("client1")
        allowed, remaining = limiter.check("client1")
        assert allowed is True
        assert remaining == 0

    def test_over_limit_denied(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.check("client1")
        allowed, remaining = limiter.check("client1")
        assert allowed is False
        assert remaining == 0

    def test_remaining_without_recording(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        limiter.check("client1")
        limiter.check("client1")
        assert limiter.remaining("client1") == 3

    def test_different_clients_independent(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("client1")
        limiter.check("client1")
        allowed, _ = limiter.check("client2")
        assert allowed is True
