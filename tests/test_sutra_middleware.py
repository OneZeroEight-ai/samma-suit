"""Tests for SUTRA middleware — origin, rate limiting, TLS, headers."""

import pytest


class TestOriginValidation:
    @pytest.mark.asyncio
    async def test_allowed_origin_passes(self, client):
        resp = await client.get("/api/test", headers={"origin": "https://onezeroeight.ai"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_disallowed_origin_returns_403(self, client):
        resp = await client.get("/api/test", headers={"origin": "https://evil.com"})
        assert resp.status_code == 403
        assert "Origin not allowed" in resp.json()["detail"]
        assert resp.json()["layer"] == "sutra"

    @pytest.mark.asyncio
    async def test_glob_origin_matches(self, client):
        resp = await client.get("/api/test", headers={"origin": "https://app.sutra.team"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_no_origin_header_passes(self, client):
        resp = await client.get("/api/test")
        assert resp.status_code == 200


class TestRateLimiting:
    @pytest.mark.asyncio
    async def test_under_limit_passes(self, client):
        for _ in range(5):
            resp = await client.get("/api/test")
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_over_limit_returns_429(self, client):
        # Limit is 5 per window
        for _ in range(5):
            await client.get("/api/test")
        resp = await client.get("/api/test")
        assert resp.status_code == 429
        assert resp.json()["layer"] == "sutra"
        assert "retry-after" in resp.headers

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, client):
        resp = await client.get("/api/test")
        assert "x-ratelimit-remaining" in resp.headers


class TestExcludedPaths:
    @pytest.mark.asyncio
    async def test_health_bypasses_checks(self, client):
        # Health should work even with bad origin
        resp = await client.get("/health", headers={"origin": "https://evil.com"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_excluded_path_still_has_layer_header(self, client):
        resp = await client.get("/health")
        assert resp.headers.get("x-samma-layer") == "sutra"


class TestResponseHeaders:
    @pytest.mark.asyncio
    async def test_samma_layer_header(self, client):
        resp = await client.get("/api/test")
        assert resp.headers.get("x-samma-layer") == "sutra"
