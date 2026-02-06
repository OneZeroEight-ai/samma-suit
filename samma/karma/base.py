"""KARMA base — ABC and models for cost controls (Layer 4)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentBudget(BaseModel):
    """Budget allocation for an agent."""

    agent_id: str
    daily_limit: float = 0.0
    monthly_limit: float = 0.0
    spent_today: float = 0.0
    spent_this_month: float = 0.0
    currency: str = "USD"
    last_reset: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def remaining_today(self) -> float:
        return max(0.0, self.daily_limit - self.spent_today)

    @property
    def remaining_this_month(self) -> float:
        return max(0.0, self.monthly_limit - self.spent_this_month)


class CostController(ABC):
    """Abstract base for cost control implementations."""

    @abstractmethod
    async def check_budget(self, agent_id: str, estimated_cost: float) -> bool:
        """Check if an agent has budget for an operation. Returns True if allowed."""
        ...

    @abstractmethod
    async def record_spend(self, agent_id: str, amount: float, description: str = "") -> AgentBudget:
        """Record a spend against an agent's budget."""
        ...

    @abstractmethod
    async def get_balance(self, agent_id: str) -> AgentBudget:
        """Get current budget status for an agent."""
        ...

    @abstractmethod
    async def set_budget(self, agent_id: str, daily_limit: float, monthly_limit: float) -> AgentBudget:
        """Set budget limits for an agent."""
        ...
