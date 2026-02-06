"""Policy engine — resolution order: explicit deny > explicit grant > role > default-deny."""

from __future__ import annotations

import logging
from typing import Optional

from samma.dharma.config import DHARMASettings
from samma.dharma.permissions import Permission, PermissionSet
from samma.dharma.roles import RoleRegistry
from samma.exceptions import PermissionDeniedError

logger = logging.getLogger("samma.dharma.policy")


class PolicyEngine:
    """
    Resolves permissions for an agent using:
        1. Explicit denials (always win)
        2. Explicit grants (per-agent overrides)
        3. Role-based permissions (from RoleRegistry)
        4. Default-deny (if nothing grants the permission)
    """

    def __init__(
        self,
        role_registry: RoleRegistry | None = None,
        settings: DHARMASettings | None = None,
    ) -> None:
        self.roles = role_registry or RoleRegistry()
        self.settings = settings or DHARMASettings()
        # Per-agent overrides: agent_id -> (grants, denials)
        self._grants: dict[str, PermissionSet] = {}
        self._denials: dict[str, PermissionSet] = {}

    def grant(self, agent_id: str, *perms: Permission) -> None:
        """Add explicit grants for an agent (beyond their role)."""
        existing = self._grants.get(agent_id, PermissionSet())
        self._grants[agent_id] = existing.union(PermissionSet(perms))

    def deny(self, agent_id: str, *perms: Permission) -> None:
        """Add explicit denials for an agent (override role grants)."""
        existing = self._denials.get(agent_id, PermissionSet())
        self._denials[agent_id] = existing.union(PermissionSet(perms))

    def check(
        self,
        agent_id: str,
        agent_type: str,
        permission: Permission,
    ) -> bool:
        """
        Check if an agent has a permission. Does not raise.

        Resolution order:
            1. Explicit denial → False
            2. Explicit grant → True
            3. Role permission → True
            4. Default-deny → False
        """
        # 1. Explicit denials
        denials = self._denials.get(agent_id, PermissionSet())
        if permission in denials:
            if self.settings.log_denials:
                logger.info(
                    "DHARMA DENIED (explicit) %s for agent %s (%s)",
                    permission.value, agent_id, agent_type,
                )
            return False

        # 2. Explicit grants
        grants = self._grants.get(agent_id, PermissionSet())
        if permission in grants:
            if self.settings.log_grants:
                logger.info(
                    "DHARMA GRANTED (explicit) %s for agent %s (%s)",
                    permission.value, agent_id, agent_type,
                )
            return True

        # 3. Role-based permissions
        role = self.roles.get(agent_type)
        if role and permission in role.permissions:
            if self.settings.log_grants:
                logger.info(
                    "DHARMA GRANTED (role:%s) %s for agent %s",
                    role.name, permission.value, agent_id,
                )
            return True

        # 4. Default-deny
        if self.settings.log_denials:
            logger.info(
                "DHARMA DENIED (default-deny) %s for agent %s (%s)",
                permission.value, agent_id, agent_type,
            )
        return False

    def require(
        self,
        agent_id: str,
        agent_type: str,
        permission: Permission,
    ) -> None:
        """Check permission and raise PermissionDeniedError if denied."""
        if not self.check(agent_id, agent_type, permission):
            raise PermissionDeniedError(
                f"Agent {agent_id} ({agent_type}) lacks permission: {permission.value}"
            )

    def get_effective_permissions(
        self,
        agent_id: str,
        agent_type: str,
    ) -> PermissionSet:
        """Return the full set of effective permissions for an agent."""
        # Start with role permissions
        role = self.roles.get(agent_type)
        role_perms = role.permissions if role else PermissionSet()

        # Add explicit grants
        grants = self._grants.get(agent_id, PermissionSet())
        combined = role_perms.union(grants)

        # Remove explicit denials
        denials = self._denials.get(agent_id, PermissionSet())
        return combined.difference(denials)
