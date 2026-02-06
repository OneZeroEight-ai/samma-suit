"""SUTRA middleware — Starlette BaseHTTPMiddleware for gateway enforcement."""

from __future__ import annotations

import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from samma.exceptions import OriginDeniedError, RateLimitExceededError, TLSRequiredError
from samma.sutra.config import SUTRASettings
from samma.sutra.origin_validator import OriginValidator
from samma.sutra.rate_limiter import RateLimiter
from samma.sutra.tls_checker import TLSChecker

logger = logging.getLogger("samma.sutra")


class SUTRAMiddleware(BaseHTTPMiddleware):
    """
    SUTRA Gateway Middleware.

    Performs origin validation, rate limiting, and TLS checking
    on every request (except excluded paths).
    """

    def __init__(self, app, settings: SUTRASettings | None = None) -> None:
        super().__init__(app)
        self.settings = settings or SUTRASettings()
        self.origin_validator = OriginValidator(self.settings.allowed_origins)
        self.ip_limiter = RateLimiter(
            max_requests=self.settings.rate_limit_per_ip,
            window_seconds=self.settings.rate_limit_window_seconds,
        )
        self.agent_limiter = RateLimiter(
            max_requests=self.settings.rate_limit_per_agent,
            window_seconds=self.settings.rate_limit_window_seconds,
        )
        self.tls_checker = TLSChecker(
            enforce=self.settings.tls_enforce,
            warn=self.settings.tls_warn,
        )
        logger.info(
            "SUTRA middleware initialized (rate_limit=%d/%ds, origins=%s)",
            self.settings.rate_limit_per_ip,
            self.settings.rate_limit_window_seconds,
            len(self.settings.allowed_origins),
        )

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_excluded(self, path: str) -> bool:
        return path in self.settings.excluded_paths

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.monotonic()
        path = request.url.path

        # Skip excluded paths
        if self._is_excluded(path):
            response = await call_next(request)
            response.headers["X-Samma-Layer"] = "sutra"
            return response

        client_ip = self._get_client_ip(request)
        origin = request.headers.get("origin")
        agent_id = request.headers.get("x-agent-id")

        # 1. TLS check
        try:
            self.tls_checker.check(
                scheme=str(request.url.scheme),
                forwarded_proto=request.headers.get("x-forwarded-proto"),
            )
        except TLSRequiredError:
            return JSONResponse(
                status_code=403,
                content={"detail": "HTTPS required", "layer": "sutra"},
            )

        # 2. Origin validation
        try:
            self.origin_validator.validate(origin)
        except OriginDeniedError:
            logger.warning("SUTRA origin denied: %s from %s", origin, client_ip)
            return JSONResponse(
                status_code=403,
                content={"detail": f"Origin not allowed: {origin}", "layer": "sutra"},
            )

        # 3. Rate limiting (per-IP)
        ip_allowed, ip_remaining = self.ip_limiter.check(f"ip:{client_ip}")
        if not ip_allowed:
            logger.warning("SUTRA rate limit exceeded for IP %s on %s", client_ip, path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "layer": "sutra"},
                headers={
                    "Retry-After": str(self.settings.rate_limit_window_seconds),
                    "X-Samma-Layer": "sutra",
                },
            )

        # 4. Rate limiting (per-agent, if agent header present)
        agent_remaining = None
        if agent_id:
            agent_allowed, agent_remaining = self.agent_limiter.check(f"agent:{agent_id}")
            if not agent_allowed:
                logger.warning("SUTRA rate limit exceeded for agent %s", agent_id)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Agent rate limit exceeded", "layer": "sutra"},
                    headers={
                        "Retry-After": str(self.settings.rate_limit_window_seconds),
                        "X-Samma-Layer": "sutra",
                    },
                )

        # Process request
        response = await call_next(request)

        # Response headers
        duration_ms = (time.monotonic() - start) * 1000
        response.headers["X-Samma-Layer"] = "sutra"
        response.headers["X-RateLimit-Remaining"] = str(ip_remaining)
        if agent_remaining is not None:
            response.headers["X-RateLimit-Agent-Remaining"] = str(agent_remaining)

        # Request logging
        if self.settings.log_requests:
            logger.info(
                "SUTRA %s %s [%s] origin=%s status=%d %.1fms",
                request.method,
                path,
                client_ip,
                origin or "-",
                response.status_code,
                duration_ms,
            )

        return response
