"""TLS enforcement — checks HTTPS via X-Forwarded-Proto (Railway/proxy aware)."""

from __future__ import annotations

import logging

from samma.exceptions import TLSRequiredError

logger = logging.getLogger("samma.sutra.tls")


class TLSChecker:
    """Checks that requests arrive over HTTPS."""

    def __init__(self, enforce: bool = False, warn: bool = True) -> None:
        self.enforce = enforce
        self.warn = warn

    def is_secure(self, scheme: str | None, forwarded_proto: str | None) -> bool:
        """Check if the request is over HTTPS (direct or behind proxy)."""
        if forwarded_proto:
            return forwarded_proto.lower() == "https"
        if scheme:
            return scheme.lower() == "https"
        return False

    def check(self, scheme: str | None, forwarded_proto: str | None) -> None:
        """Warn or raise if the request is not HTTPS."""
        if self.is_secure(scheme, forwarded_proto):
            return
        msg = "Request is not over HTTPS"
        if self.enforce:
            raise TLSRequiredError(msg)
        if self.warn:
            logger.warning("SUTRA TLS warning: %s", msg)
