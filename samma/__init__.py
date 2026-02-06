"""
Samma Suit SDK — 8-layer security framework for AI agent systems.

Layers:
    1. SUTRA   — Gateway (rate limiting, origin validation, TLS)
    2. DHARMA  — Permissions (roles, policy engine, default-deny)
    3. SANGHA  — Skill Vetting (stub)
    4. KARMA   — Cost Controls (stub)
    5. SILA    — Audit Trail (stub)
    6. METTA   — Identity (stub)
    7. BODHI   — Isolation (stub)
    8. NIRVANA — Recovery (stub)
"""

from samma._version import __version__
from samma.exceptions import SammaError
from samma.types import AgentIdentity, LayerStatus, SecurityEvent

# SUTRA (Layer 1)
from samma.sutra.config import SUTRASettings
from samma.sutra.middleware import SUTRAMiddleware

# DHARMA (Layer 2)
from samma.dharma.config import DHARMASettings
from samma.dharma.permissions import Permission, PermissionSet
from samma.dharma.roles import Role, RoleRegistry
from samma.dharma.policy import PolicyEngine
from samma.dharma.dependencies import require_permission
from samma.dharma.decorators import dharma_protected

# Integration
from samma.fastapi.integration import SammaSuit

__all__ = [
    "__version__",
    "SammaError",
    "AgentIdentity",
    "LayerStatus",
    "SecurityEvent",
    "SUTRASettings",
    "SUTRAMiddleware",
    "DHARMASettings",
    "Permission",
    "PermissionSet",
    "Role",
    "RoleRegistry",
    "PolicyEngine",
    "require_permission",
    "dharma_protected",
    "SammaSuit",
]
