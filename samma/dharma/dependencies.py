"""FastAPI Depends() helpers for DHARMA permission checks."""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from samma.dharma.permissions import Permission
from samma.dharma.policy import PolicyEngine
from samma.exceptions import PermissionDeniedError

logger = logging.getLogger("samma.dharma.deps")

# Module-level policy engine — set by SammaSuit.activate_dharma()
_policy_engine: Optional[PolicyEngine] = None
_agent_header: str = "x-agent-id"
_agent_type_header: str = "x-agent-type"


def set_policy_engine(engine: PolicyEngine) -> None:
    """Set the global policy engine (called by SammaSuit)."""
    global _policy_engine
    _policy_engine = engine


def set_headers(agent_header: str, agent_type_header: str) -> None:
    """Configure which HTTP headers carry agent identity."""
    global _agent_header, _agent_type_header
    _agent_header = agent_header
    _agent_type_header = agent_type_header


def require_permission(permission: Permission) -> Callable:
    """
    FastAPI Depends() factory that checks an agent has a specific permission.

    Usage:
        @app.get("/endpoint")
        async def endpoint(
            _perm=Depends(require_permission(Permission.EMAIL_SEND)),
        ):
            ...

    The agent identity is read from X-Agent-Id and X-Agent-Type headers.
    If no agent headers are present, the request passes through (host-app traffic).
    """

    async def _check(request: Any) -> None:
        if _policy_engine is None:
            return  # DHARMA not activated — pass through

        # Import Request lazily to avoid hard dep on starlette at import time
        agent_id = request.headers.get(_agent_header)
        agent_type = request.headers.get(_agent_type_header)

        if not agent_id or not agent_type:
            # No agent identity — not an agent request, pass through
            return

        if not _policy_engine.check(agent_id, agent_type, permission):
            raise PermissionDeniedError(
                f"Agent {agent_id} ({agent_type}) lacks permission: {permission.value}"
            )

    # Annotate so FastAPI treats request as a Request dependency
    try:
        from fastapi import Request
        import inspect

        # Create a proper dependency with Request parameter
        sig = inspect.signature(_check)
        new_params = [
            inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request)
        ]
        _check.__signature__ = sig.replace(parameters=new_params)
    except ImportError:
        pass

    return _check
