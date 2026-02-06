"""Shared fixtures for Samma Suit tests."""

import pytest
import httpx
from httpx._transports.asgi import ASGITransport
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from samma import SammaSuit, SUTRASettings
from samma.dharma.config import DHARMASettings
from samma.dharma.dependencies import require_permission
from samma.dharma.permissions import Permission
from samma.dharma.policy import PolicyEngine
from samma.dharma.roles import RoleRegistry
from samma.exceptions import PermissionDeniedError


@pytest.fixture
def sutra_settings():
    return SUTRASettings(
        allowed_origins=["https://onezeroeight.ai", "https://*.sutra.team"],
        rate_limit_per_ip=5,
        rate_limit_per_agent=10,
        rate_limit_window_seconds=60,
        tls_enforce=False,
        tls_warn=False,
        log_requests=False,
    )


@pytest.fixture
def dharma_settings():
    return DHARMASettings(
        default_deny=True,
        log_denials=False,
        log_grants=False,
    )


@pytest.fixture
def role_registry():
    return RoleRegistry()


@pytest.fixture
def policy_engine(role_registry, dharma_settings):
    return PolicyEngine(role_registry=role_registry, settings=dharma_settings)


@pytest.fixture
def test_app(sutra_settings, dharma_settings):
    """Create a FastAPI app with SUTRA + DHARMA activated."""
    app = FastAPI()

    suit = SammaSuit(app)
    suit.activate_sutra(settings=sutra_settings)
    suit.activate_dharma(settings=dharma_settings)

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.get("/api/test")
    async def test_endpoint():
        return {"message": "ok"}

    @app.get("/api/protected")
    async def protected_endpoint(
        _perm=Depends(require_permission(Permission.ADMIN_WRITE)),
    ):
        return {"message": "admin access granted"}

    @app.get("/api/agent-view")
    async def agent_view_endpoint(
        _perm=Depends(require_permission(Permission.AGENT_VIEW)),
    ):
        return {"message": "agent view granted"}

    @app.get("/samma/status")
    async def samma_status():
        return suit.status()

    # Exception handler for PermissionDeniedError
    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc), "layer": "dharma"},
        )

    return app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
