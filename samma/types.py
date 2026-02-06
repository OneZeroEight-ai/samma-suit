"""Core types shared across all Samma Suit layers."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentIdentity(BaseModel):
    """
    Represents an authenticated agent passing through the Samma Suit.
    Populated by the host app (database-agnostic).
    """

    agent_id: str
    agent_type: str  # matches AgentType enum values: "playlist", "sutra", "dharma", etc.
    name: str = ""
    is_system: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class SecurityEventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class SecurityEvent(BaseModel):
    """A security-relevant event emitted by any Samma layer."""

    layer: str
    event_type: str
    severity: SecurityEventSeverity = SecurityEventSeverity.INFO
    agent_id: Optional[str] = None
    ip_address: Optional[str] = None
    detail: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LayerStatus(BaseModel):
    """Status report for a single Samma layer."""

    name: str
    active: bool = False
    version: str = "0.1.0"
    detail: str = ""
