"""Decorator for protecting endpoints with DHARMA permissions."""

from __future__ import annotations

import functools
from typing import Callable

from samma.dharma.permissions import Permission
from samma.dharma.dependencies import _policy_engine, _agent_header, _agent_type_header
from samma.exceptions import PermissionDeniedError


def dharma_protected(*permissions: Permission) -> Callable:
    """
    Decorator that checks agent permissions before executing a route handler.

    Usage:
        @app.get("/endpoint")
        @dharma_protected(Permission.EMAIL_SEND)
        async def endpoint(request: Request):
            ...

    If no agent headers are present, the request passes through.
    If the agent lacks any of the required permissions, raises PermissionDeniedError.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the Request object in args/kwargs
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if hasattr(arg, "headers"):
                        request = arg
                        break

            if request is not None and _policy_engine is not None:
                agent_id = request.headers.get(_agent_header)
                agent_type = request.headers.get(_agent_type_header)

                if agent_id and agent_type:
                    for perm in permissions:
                        if not _policy_engine.check(agent_id, agent_type, perm):
                            raise PermissionDeniedError(
                                f"Agent {agent_id} ({agent_type}) lacks permission: {perm.value}"
                            )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
