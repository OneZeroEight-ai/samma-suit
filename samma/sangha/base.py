"""SANGHA base — ABC and models for skill vetting (Layer 3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SkillStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"


class SkillManifest(BaseModel):
    """Describes a skill/tool an agent wants to use."""

    skill_id: str
    name: str
    description: str = ""
    version: str = "0.1.0"
    author: str = ""
    permissions_required: list[str] = Field(default_factory=list)
    status: SkillStatus = SkillStatus.PENDING
    scanned_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillVetter(ABC):
    """Abstract base for skill vetting implementations."""

    @abstractmethod
    async def scan_skill(self, manifest: SkillManifest) -> dict[str, Any]:
        """Scan a skill for security issues. Returns findings dict."""
        ...

    @abstractmethod
    async def sandbox_test(self, manifest: SkillManifest) -> bool:
        """Run a skill in a sandbox and verify behavior. Returns pass/fail."""
        ...

    @abstractmethod
    async def approve_skill(self, skill_id: str) -> SkillManifest:
        """Mark a skill as approved for production use."""
        ...

    @abstractmethod
    async def revoke_skill(self, skill_id: str) -> SkillManifest:
        """Revoke approval for a skill."""
        ...
