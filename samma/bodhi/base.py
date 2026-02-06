"""BODHI base — ABC and models for isolation/sandboxing (Layer 7)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class IsolationLevel(str, Enum):
    NONE = "none"
    PROCESS = "process"
    CONTAINER = "container"
    VM = "vm"


class SandboxConfig(BaseModel):
    """Configuration for an agent sandbox."""

    agent_id: str
    isolation_level: IsolationLevel = IsolationLevel.PROCESS
    max_memory_mb: int = 512
    max_cpu_seconds: int = 30
    network_allowed: bool = False
    allowed_egress: list[str] = Field(default_factory=list)
    filesystem_readonly: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class SandboxResult(BaseModel):
    """Result of executing something in a sandbox."""

    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    egress_attempts: list[str] = Field(default_factory=list)


class SandboxManager(ABC):
    """Abstract base for sandbox/isolation implementations."""

    @abstractmethod
    async def create_sandbox(self, config: SandboxConfig) -> str:
        """Create a sandbox. Returns sandbox ID."""
        ...

    @abstractmethod
    async def execute_in_sandbox(self, sandbox_id: str, code: str) -> SandboxResult:
        """Execute code in a sandbox."""
        ...

    @abstractmethod
    async def check_egress(self, sandbox_id: str) -> list[str]:
        """Check for unauthorized egress attempts from a sandbox."""
        ...

    @abstractmethod
    async def destroy_sandbox(self, sandbox_id: str) -> None:
        """Destroy a sandbox and clean up resources."""
        ...
