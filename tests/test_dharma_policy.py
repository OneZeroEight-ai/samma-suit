"""Tests for DHARMA policy engine — resolution order."""

import pytest
from samma.dharma.permissions import Permission
from samma.dharma.policy import PolicyEngine
from samma.exceptions import PermissionDeniedError


class TestPolicyResolutionOrder:
    """Test: explicit denial > explicit grant > role permissions > default-deny."""

    def test_role_grants_permission(self, policy_engine):
        # Playlist agents have PLAYLIST_READ via their role
        assert policy_engine.check("agent-1", "playlist", Permission.PLAYLIST_READ) is True

    def test_default_deny_blocks_unknown_permission(self, policy_engine):
        # Playlist agents don't have ADMIN_WRITE
        assert policy_engine.check("agent-1", "playlist", Permission.ADMIN_WRITE) is False

    def test_explicit_grant_overrides_default_deny(self, policy_engine):
        # Grant ADMIN_WRITE to a specific playlist agent
        policy_engine.grant("agent-1", Permission.ADMIN_WRITE)
        assert policy_engine.check("agent-1", "playlist", Permission.ADMIN_WRITE) is True

    def test_explicit_denial_overrides_role_grant(self, policy_engine):
        # Playlist agents have PLAYLIST_READ via role, but deny it for agent-1
        policy_engine.deny("agent-1", Permission.PLAYLIST_READ)
        assert policy_engine.check("agent-1", "playlist", Permission.PLAYLIST_READ) is False

    def test_explicit_denial_overrides_explicit_grant(self, policy_engine):
        # Grant then deny the same permission
        policy_engine.grant("agent-1", Permission.SHELL_EXEC)
        policy_engine.deny("agent-1", Permission.SHELL_EXEC)
        assert policy_engine.check("agent-1", "playlist", Permission.SHELL_EXEC) is False

    def test_unknown_agent_type_default_deny(self, policy_engine):
        # Unknown agent type has no role → default-deny
        assert policy_engine.check("agent-x", "unknown_type", Permission.FILE_READ) is False

    def test_admin_has_all_permissions(self, policy_engine):
        assert policy_engine.check("admin-1", "admin", Permission.ADMIN_WRITE) is True
        assert policy_engine.check("admin-1", "admin", Permission.SHELL_EXEC) is True
        assert policy_engine.check("admin-1", "admin", Permission.DB_DELETE) is True


class TestPolicyRequire:
    def test_require_passes_when_allowed(self, policy_engine):
        # Should not raise
        policy_engine.require("agent-1", "playlist", Permission.PLAYLIST_READ)

    def test_require_raises_when_denied(self, policy_engine):
        with pytest.raises(PermissionDeniedError):
            policy_engine.require("agent-1", "playlist", Permission.ADMIN_WRITE)


class TestEffectivePermissions:
    def test_effective_permissions_from_role(self, policy_engine):
        perms = policy_engine.get_effective_permissions("agent-1", "playlist")
        assert Permission.PLAYLIST_READ in perms
        assert Permission.ADMIN_WRITE not in perms

    def test_effective_permissions_with_grant(self, policy_engine):
        policy_engine.grant("agent-1", Permission.SHELL_EXEC)
        perms = policy_engine.get_effective_permissions("agent-1", "playlist")
        assert Permission.SHELL_EXEC in perms

    def test_effective_permissions_with_denial(self, policy_engine):
        policy_engine.deny("agent-1", Permission.PLAYLIST_READ)
        perms = policy_engine.get_effective_permissions("agent-1", "playlist")
        assert Permission.PLAYLIST_READ not in perms

    def test_effective_permissions_unknown_type(self, policy_engine):
        perms = policy_engine.get_effective_permissions("agent-x", "unknown")
        assert len(perms) == 0
