"""Integration tests — SUTRA + DHARMA together."""

import pytest


class TestSammaStatus:
    @pytest.mark.asyncio
    async def test_status_endpoint(self, client):
        resp = await client.get("/samma/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["samma_version"] == "0.1.1"
        assert data["active_count"] == 2  # sutra + dharma
        assert data["total_layers"] == 8
        assert data["layers"]["sutra"]["active"] is True
        assert data["layers"]["dharma"]["active"] is True
        assert data["layers"]["sangha"]["active"] is False


class TestSutraAndDharmaTogether:
    @pytest.mark.asyncio
    async def test_valid_origin_no_agent_passes(self, client):
        """Non-agent request with valid origin should pass through."""
        resp = await client.get(
            "/api/test",
            headers={"origin": "https://onezeroeight.ai"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_bad_origin_blocked_before_dharma(self, client):
        """SUTRA blocks bad origin before DHARMA even checks permissions."""
        resp = await client.get(
            "/api/protected",
            headers={
                "origin": "https://evil.com",
                "x-agent-id": "admin-1",
                "x-agent-type": "admin",
            },
        )
        assert resp.status_code == 403
        assert resp.json()["layer"] == "sutra"

    @pytest.mark.asyncio
    async def test_agent_with_permission_passes(self, client):
        """Agent with correct permissions passes both SUTRA and DHARMA."""
        resp = await client.get(
            "/api/agent-view",
            headers={
                "origin": "https://onezeroeight.ai",
                "x-agent-id": "playlist-1",
                "x-agent-type": "playlist",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "agent view granted"

    @pytest.mark.asyncio
    async def test_agent_without_permission_denied(self, client):
        """Agent lacking required permission gets DHARMA 403."""
        resp = await client.get(
            "/api/protected",
            headers={
                "origin": "https://onezeroeight.ai",
                "x-agent-id": "playlist-1",
                "x-agent-type": "playlist",
            },
        )
        assert resp.status_code == 403
        assert resp.json()["layer"] == "dharma"

    @pytest.mark.asyncio
    async def test_admin_agent_passes_protected_route(self, client):
        """Admin agent passes all permission checks."""
        resp = await client.get(
            "/api/protected",
            headers={
                "origin": "https://onezeroeight.ai",
                "x-agent-id": "admin-1",
                "x-agent-type": "admin",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "admin access granted"

    @pytest.mark.asyncio
    async def test_non_agent_request_passes_protected(self, client):
        """Request without agent headers passes DHARMA (host-app traffic)."""
        resp = await client.get(
            "/api/protected",
            headers={"origin": "https://onezeroeight.ai"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_applies_to_all_routes(self, client):
        """Rate limiting from SUTRA applies even to DHARMA-protected routes."""
        for _ in range(5):
            await client.get("/api/test")
        resp = await client.get(
            "/api/protected",
            headers={
                "origin": "https://onezeroeight.ai",
                "x-agent-id": "admin-1",
                "x-agent-type": "admin",
            },
        )
        assert resp.status_code == 429


class TestPackageImports:
    def test_import_samma(self):
        from samma import SammaSuit, SUTRASettings, SUTRAMiddleware
        assert SammaSuit is not None
        assert SUTRASettings is not None

    def test_import_permissions(self):
        from samma import Permission, PermissionSet, Role, RoleRegistry
        assert Permission is not None
        assert len(Permission) >= 25

    def test_import_policy(self):
        from samma import PolicyEngine, require_permission, dharma_protected
        assert PolicyEngine is not None

    def test_version(self):
        from samma import __version__
        assert __version__ == "0.1.1"
