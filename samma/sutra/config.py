"""SUTRA configuration — Pydantic BaseSettings for gateway layer."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class SUTRASettings(BaseSettings):
    """Configuration for the SUTRA gateway layer."""

    model_config = {"env_prefix": "SUTRA_"}

    # Origin validation
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed origins (supports glob patterns like '*.onezeroeight.ai')",
    )

    # Rate limiting
    rate_limit_per_ip: int = Field(
        default=100,
        description="Max requests per IP within the window",
    )
    rate_limit_per_agent: int = Field(
        default=200,
        description="Max requests per agent within the window",
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Sliding window duration in seconds",
    )

    # TLS enforcement
    tls_enforce: bool = Field(
        default=False,
        description="Reject non-HTTPS requests (vs. warn-only)",
    )
    tls_warn: bool = Field(
        default=True,
        description="Log warning for non-HTTPS requests",
    )

    # Excluded paths (bypass all SUTRA checks)
    excluded_paths: list[str] = Field(
        default_factory=lambda: ["/health", "/docs", "/openapi.json", "/redoc", "/"],
    )

    # Logging
    log_requests: bool = Field(default=True)
