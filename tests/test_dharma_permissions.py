"""Tests for DHARMA permissions — grants, denials, roles."""

import pytest
from samma.dharma.permissions import Permission, PermissionSet
from samma.dharma.roles import (
    Role, RoleRegistry,
    ROLE_PLAYLIST, ROLE_SUTRA, ROLE_DHARMA, ROLE_ADMIN,
)


class TestPermissionSet:
    def test_has_permission(self):
        ps = PermissionSet([Permission.FILE_READ, Permission.FILE_WRITE])
        assert ps.has(Permission.FILE_READ)
        assert not ps.has(Permission.SHELL_EXEC)

    def test_contains(self):
        ps = PermissionSet([Permission.FILE_READ])
        assert Permission.FILE_READ in ps
        assert Permission.FILE_WRITE not in ps

    def test_has_all(self):
        ps = PermissionSet([Permission.FILE_READ, Permission.FILE_WRITE, Permission.DB_READ])
        assert ps.has_all([Permission.FILE_READ, Permission.FILE_WRITE])
        assert not ps.has_all([Permission.FILE_READ, Permission.SHELL_EXEC])

    def test_has_any(self):
        ps = PermissionSet([Permission.FILE_READ])
        assert ps.has_any([Permission.FILE_READ, Permission.SHELL_EXEC])
        assert not ps.has_any([Permission.SHELL_EXEC, Permission.DB_DELETE])

    def test_union(self):
        ps1 = PermissionSet([Permission.FILE_READ])
        ps2 = PermissionSet([Permission.FILE_WRITE])
        combined = ps1.union(ps2)
        assert Permission.FILE_READ in combined
        assert Permission.FILE_WRITE in combined

    def test_difference(self):
        ps1 = PermissionSet([Permission.FILE_READ, Permission.FILE_WRITE])
        ps2 = PermissionSet([Permission.FILE_WRITE])
        diff = ps1.difference(ps2)
        assert Permission.FILE_READ in diff
        assert Permission.FILE_WRITE not in diff

    def test_len(self):
        ps = PermissionSet([Permission.FILE_READ, Permission.FILE_WRITE])
        assert len(ps) == 2

    def test_empty(self):
        ps = PermissionSet()
        assert len(ps) == 0
        assert not ps.has(Permission.FILE_READ)


class TestDefaultRoles:
    def test_playlist_has_expected_permissions(self):
        assert ROLE_PLAYLIST.permissions.has(Permission.PLAYLIST_READ)
        assert ROLE_PLAYLIST.permissions.has(Permission.PLAYLIST_WRITE)
        assert ROLE_PLAYLIST.permissions.has(Permission.SUTRA_EARN)
        assert not ROLE_PLAYLIST.permissions.has(Permission.ADMIN_WRITE)

    def test_sutra_has_system_permissions(self):
        assert ROLE_SUTRA.permissions.has(Permission.SUTRA_EARN)
        assert ROLE_SUTRA.permissions.has(Permission.SUTRA_TRANSFER)
        assert ROLE_SUTRA.permissions.has(Permission.AGENT_MANAGE)
        assert not ROLE_SUTRA.permissions.has(Permission.ADMIN_WRITE)

    def test_dharma_has_hr_permissions(self):
        assert ROLE_DHARMA.permissions.has(Permission.AGENT_MANAGE)
        assert ROLE_DHARMA.permissions.has(Permission.AGENT_SPAWN)
        assert ROLE_DHARMA.permissions.has(Permission.ADMIN_READ)
        assert not ROLE_DHARMA.permissions.has(Permission.ADMIN_WRITE)

    def test_admin_has_all_permissions(self):
        for perm in Permission:
            assert ROLE_ADMIN.permissions.has(perm)


class TestRoleRegistry:
    def test_default_roles_loaded(self, role_registry):
        assert "playlist" in role_registry
        assert "sutra" in role_registry
        assert "dharma" in role_registry
        assert "admin" in role_registry

    def test_get_role(self, role_registry):
        role = role_registry.get("playlist")
        assert role is not None
        assert role.name == "playlist"

    def test_unknown_role_returns_none(self, role_registry):
        assert role_registry.get("unknown") is None

    def test_register_custom_role(self, role_registry):
        custom = Role(
            name="custom",
            description="Custom test role",
            permissions=PermissionSet([Permission.FILE_READ]),
        )
        role_registry.register(custom)
        assert "custom" in role_registry
        assert role_registry.get("custom").permissions.has(Permission.FILE_READ)

    def test_list_roles(self, role_registry):
        roles = role_registry.list_roles()
        names = {r.name for r in roles}
        assert "playlist" in names
        assert "admin" in names
