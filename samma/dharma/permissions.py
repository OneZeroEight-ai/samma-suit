"""Permission definitions — 25+ permission types for agent operations."""

from __future__ import annotations

from enum import Enum
from typing import Iterable


class Permission(str, Enum):
    """All permission types in the Samma Suit system."""

    # File operations
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"

    # Shell / execution
    SHELL_EXEC = "shell_exec"
    PROCESS_SPAWN = "process_spawn"

    # Communication
    EMAIL_SEND = "email_send"
    NOTIFICATION_SEND = "notification_send"
    WEBHOOK_CALL = "webhook_call"

    # SUTRA token operations
    SUTRA_EARN = "sutra_earn"
    SUTRA_TRANSFER = "sutra_transfer"
    SUTRA_VIEW = "sutra_view"

    # Database operations
    DB_READ = "db_read"
    DB_WRITE = "db_write"
    DB_DELETE = "db_delete"

    # Agent operations
    AGENT_SPAWN = "agent_spawn"
    AGENT_MANAGE = "agent_manage"
    AGENT_VIEW = "agent_view"

    # Admin operations
    ADMIN_READ = "admin_read"
    ADMIN_WRITE = "admin_write"
    ADMIN_DELETE = "admin_delete"

    # Artist / campaign operations
    ARTIST_READ = "artist_read"
    ARTIST_WRITE = "artist_write"
    CAMPAIGN_READ = "campaign_read"
    CAMPAIGN_WRITE = "campaign_write"

    # Curator operations
    CURATOR_READ = "curator_read"
    CURATOR_WRITE = "curator_write"

    # Playlist operations
    PLAYLIST_READ = "playlist_read"
    PLAYLIST_WRITE = "playlist_write"

    # External API calls
    API_EXTERNAL = "api_external"

    # Social media operations
    SOCIAL_POST = "social_post"
    SOCIAL_READ = "social_read"

    # PR operations
    PR_OUTREACH = "pr_outreach"
    PR_READ = "pr_read"


class PermissionSet:
    """An immutable set of permissions."""

    def __init__(self, permissions: Iterable[Permission] = ()) -> None:
        self._perms = frozenset(permissions)

    def has(self, perm: Permission) -> bool:
        return perm in self._perms

    def has_all(self, perms: Iterable[Permission]) -> bool:
        return all(p in self._perms for p in perms)

    def has_any(self, perms: Iterable[Permission]) -> bool:
        return any(p in self._perms for p in perms)

    def union(self, other: PermissionSet) -> PermissionSet:
        return PermissionSet(self._perms | other._perms)

    def difference(self, other: PermissionSet) -> PermissionSet:
        return PermissionSet(self._perms - other._perms)

    def __contains__(self, perm: Permission) -> bool:
        return perm in self._perms

    def __iter__(self):
        return iter(self._perms)

    def __len__(self) -> int:
        return len(self._perms)

    def __repr__(self) -> str:
        names = sorted(p.value for p in self._perms)
        return f"PermissionSet({names})"
