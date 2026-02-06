"""DHARMA — Layer 2: Permissions (roles, policy engine, default-deny)."""

from samma.dharma.config import DHARMASettings
from samma.dharma.permissions import Permission, PermissionSet
from samma.dharma.roles import Role, RoleRegistry
from samma.dharma.policy import PolicyEngine
from samma.dharma.dependencies import require_permission
from samma.dharma.decorators import dharma_protected

__all__ = [
    "DHARMASettings",
    "Permission",
    "PermissionSet",
    "Role",
    "RoleRegistry",
    "PolicyEngine",
    "require_permission",
    "dharma_protected",
]
