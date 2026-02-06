"""Origin validation with glob pattern support."""

from __future__ import annotations

import fnmatch

from samma.exceptions import OriginDeniedError


class OriginValidator:
    """Validates request origins against an allowlist with glob patterns."""

    def __init__(self, allowed_origins: list[str]) -> None:
        self._patterns = allowed_origins

    @property
    def allow_all(self) -> bool:
        return "*" in self._patterns

    def is_allowed(self, origin: str | None) -> bool:
        """Check if an origin is allowed. None origin (no header) is allowed."""
        if origin is None:
            return True
        if self.allow_all:
            return True
        return any(fnmatch.fnmatch(origin, pat) for pat in self._patterns)

    def validate(self, origin: str | None) -> None:
        """Raise OriginDeniedError if origin is not allowed."""
        if not self.is_allowed(origin):
            raise OriginDeniedError(f"Origin not allowed: {origin}")
