"""METTA base — ABC and models for identity management (Layer 6)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentCertificate(BaseModel):
    """Cryptographic identity certificate for an agent."""

    agent_id: str
    public_key: str = ""
    fingerprint: str = ""
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    issuer: str = "samma-metta"
    revoked: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        if self.revoked:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True


class IdentityManager(ABC):
    """Abstract base for identity management implementations."""

    @abstractmethod
    async def register_identity(self, agent_id: str) -> AgentCertificate:
        """Register a new agent identity and generate a certificate."""
        ...

    @abstractmethod
    async def sign_message(self, agent_id: str, message: str) -> str:
        """Sign a message with an agent's private key. Returns signature."""
        ...

    @abstractmethod
    async def verify_signature(self, agent_id: str, message: str, signature: str) -> bool:
        """Verify a message signature against an agent's public key."""
        ...

    @abstractmethod
    async def revoke_identity(self, agent_id: str) -> AgentCertificate:
        """Revoke an agent's identity certificate."""
        ...
