"""SILA base — ABC and models for audit trail (Layer 5)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AuditSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuditEvent(BaseModel):
    """An auditable event in the system."""

    event_id: str = ""
    layer: str
    event_type: str
    severity: AuditSeverity = AuditSeverity.INFO
    agent_id: Optional[str] = None
    ip_address: Optional[str] = None
    action: str = ""
    resource: str = ""
    outcome: str = ""
    detail: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Auditor(ABC):
    """Abstract base for audit trail implementations."""

    @abstractmethod
    async def log_event(self, event: AuditEvent) -> str:
        """Log an audit event. Returns event ID."""
        ...

    @abstractmethod
    async def detect_anomaly(self, agent_id: str, window_minutes: int = 60) -> list[AuditEvent]:
        """Detect anomalous patterns for an agent within a time window."""
        ...

    @abstractmethod
    async def get_audit_trail(
        self, agent_id: Optional[str] = None, limit: int = 100
    ) -> list[AuditEvent]:
        """Retrieve audit events, optionally filtered by agent."""
        ...
