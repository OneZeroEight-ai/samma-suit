"""Role definitions — maps agent types to default permission sets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from samma.dharma.permissions import Permission, PermissionSet


@dataclass(frozen=True)
class Role:
    """A named role with a default permission set."""

    name: str
    description: str = ""
    permissions: PermissionSet = field(default_factory=PermissionSet)


# ── Default roles matching existing AgentType enum values ──

ROLE_PLAYLIST = Role(
    name="playlist",
    description="Playlist agent — manages artist placements",
    permissions=PermissionSet([
        Permission.PLAYLIST_READ,
        Permission.PLAYLIST_WRITE,
        Permission.ARTIST_READ,
        Permission.CAMPAIGN_READ,
        Permission.CURATOR_READ,
        Permission.SUTRA_EARN,
        Permission.SUTRA_VIEW,
        Permission.DB_READ,
        Permission.DB_WRITE,
        Permission.AGENT_VIEW,
        Permission.EMAIL_SEND,
        Permission.NOTIFICATION_SEND,
    ]),
)

ROLE_SOCIAL = Role(
    name="social",
    description="Social media agent — manages social posting",
    permissions=PermissionSet([
        Permission.SOCIAL_POST,
        Permission.SOCIAL_READ,
        Permission.ARTIST_READ,
        Permission.CAMPAIGN_READ,
        Permission.SUTRA_EARN,
        Permission.SUTRA_VIEW,
        Permission.DB_READ,
        Permission.API_EXTERNAL,
        Permission.AGENT_VIEW,
    ]),
)

ROLE_PR = Role(
    name="pr",
    description="PR agent — handles outreach and press",
    permissions=PermissionSet([
        Permission.PR_OUTREACH,
        Permission.PR_READ,
        Permission.ARTIST_READ,
        Permission.CAMPAIGN_READ,
        Permission.EMAIL_SEND,
        Permission.SUTRA_EARN,
        Permission.SUTRA_VIEW,
        Permission.DB_READ,
        Permission.API_EXTERNAL,
        Permission.AGENT_VIEW,
    ]),
)

ROLE_CURATOR = Role(
    name="curator",
    description="Curator agent — curator-facing operations",
    permissions=PermissionSet([
        Permission.CURATOR_READ,
        Permission.CURATOR_WRITE,
        Permission.PLAYLIST_READ,
        Permission.ARTIST_READ,
        Permission.SUTRA_VIEW,
        Permission.DB_READ,
        Permission.AGENT_VIEW,
    ]),
)

ROLE_SUTRA = Role(
    name="sutra",
    description="SUTRA system agent — office manager, welcomes artists/curators",
    permissions=PermissionSet([
        Permission.ARTIST_READ,
        Permission.ARTIST_WRITE,
        Permission.CURATOR_READ,
        Permission.CURATOR_WRITE,
        Permission.CAMPAIGN_READ,
        Permission.SUTRA_EARN,
        Permission.SUTRA_TRANSFER,
        Permission.SUTRA_VIEW,
        Permission.DB_READ,
        Permission.DB_WRITE,
        Permission.EMAIL_SEND,
        Permission.NOTIFICATION_SEND,
        Permission.AGENT_VIEW,
        Permission.AGENT_MANAGE,
        Permission.WEBHOOK_CALL,
    ]),
)

ROLE_DHARMA = Role(
    name="dharma",
    description="DHARMA system agent — HR manager, performance reviews",
    permissions=PermissionSet([
        Permission.AGENT_VIEW,
        Permission.AGENT_MANAGE,
        Permission.AGENT_SPAWN,
        Permission.ARTIST_READ,
        Permission.CAMPAIGN_READ,
        Permission.SUTRA_EARN,
        Permission.SUTRA_TRANSFER,
        Permission.SUTRA_VIEW,
        Permission.DB_READ,
        Permission.DB_WRITE,
        Permission.ADMIN_READ,
    ]),
)

ROLE_ADMIN = Role(
    name="admin",
    description="Admin — full system access",
    permissions=PermissionSet(list(Permission)),  # all permissions
)


class RoleRegistry:
    """Registry of all known roles. Lookup by agent_type string."""

    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}
        # Register defaults
        for role in [
            ROLE_PLAYLIST, ROLE_SOCIAL, ROLE_PR,
            ROLE_CURATOR, ROLE_SUTRA, ROLE_DHARMA, ROLE_ADMIN,
        ]:
            self._roles[role.name] = role

    def get(self, name: str) -> Optional[Role]:
        return self._roles.get(name)

    def register(self, role: Role) -> None:
        self._roles[role.name] = role

    def list_roles(self) -> list[Role]:
        return list(self._roles.values())

    def __contains__(self, name: str) -> bool:
        return name in self._roles
