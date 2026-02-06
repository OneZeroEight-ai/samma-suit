"""NIRVANA base — ABC and models for recovery/rollback (Layer 8)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class StateSnapshot(BaseModel):
    """A point-in-time snapshot of agent/system state."""

    snapshot_id: str = ""
    agent_id: Optional[str] = None
    label: str = ""
    state_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecoveryManager(ABC):
    """Abstract base for recovery/rollback implementations."""

    @abstractmethod
    async def snapshot(self, agent_id: str, label: str = "") -> StateSnapshot:
        """Take a snapshot of an agent's current state."""
        ...

    @abstractmethod
    async def rollback(self, snapshot_id: str) -> bool:
        """Rollback to a previous state snapshot. Returns success."""
        ...

    @abstractmethod
    async def kill_switch(self, agent_id: str) -> bool:
        """Emergency stop for an agent — freeze all operations."""
        ...

    @abstractmethod
    async def list_snapshots(self, agent_id: str) -> list[StateSnapshot]:
        """List available snapshots for an agent."""
        ...
