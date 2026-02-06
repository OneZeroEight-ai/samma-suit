"""DHARMA configuration — Pydantic BaseSettings for permissions layer."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class DHARMASettings(BaseSettings):
    """Configuration for the DHARMA permissions layer."""

    model_config = {"env_prefix": "DHARMA_"}

    default_deny: bool = Field(
        default=True,
        description="Deny permissions not explicitly granted (default-deny policy)",
    )
    log_denials: bool = Field(
        default=True,
        description="Log permission denial events",
    )
    log_grants: bool = Field(
        default=False,
        description="Log permission grant events (verbose)",
    )
    agent_header: str = Field(
        default="x-agent-id",
        description="HTTP header containing the agent ID",
    )
    agent_type_header: str = Field(
        default="x-agent-type",
        description="HTTP header containing the agent type",
    )
