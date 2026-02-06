"""Token-based WebSocket authentication for SUTRA layer."""

from __future__ import annotations

from typing import Any, Callable, Optional

from samma.exceptions import SUTRAError


class WebSocketAuthError(SUTRAError):
    pass


class WebSocketAuth:
    """
    Token-based WebSocket authentication.

    The host app provides a token_validator callable that takes a token string
    and returns an agent identity dict (or None if invalid).
    """

    def __init__(
        self,
        token_validator: Callable[[str], Optional[dict[str, Any]]] | None = None,
    ) -> None:
        self._validator = token_validator

    async def authenticate(self, token: str | None) -> dict[str, Any] | None:
        """
        Validate a WebSocket token.

        Returns agent identity dict if valid, None if no validator is set.
        Raises WebSocketAuthError if token is invalid.
        """
        if token is None:
            raise WebSocketAuthError("WebSocket token required")

        if self._validator is None:
            # No validator configured — pass through
            return None

        result = self._validator(token)
        if result is None:
            raise WebSocketAuthError("Invalid WebSocket token")
        return result
