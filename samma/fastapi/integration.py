"""SammaSuit — one-call FastAPI setup for all Samma layers."""

from __future__ import annotations

import logging
from typing import Optional

from samma._version import __version__
from samma.types import LayerStatus

logger = logging.getLogger("samma")


class SammaSuit:
    """
    Main entry point for integrating Samma Suit with a FastAPI app.

    Usage:
        from samma import SammaSuit, SUTRASettings

        suit = SammaSuit(app)
        suit.activate_sutra(settings=SUTRASettings(...))
        suit.activate_dharma()
    """

    def __init__(self, app=None) -> None:
        self.app = app
        self._layers: dict[str, LayerStatus] = {}
        self._sutra_middleware = None
        self._policy_engine = None

        # Register all 8 layers as inactive
        for name in [
            "sutra", "dharma", "sangha", "karma",
            "sila", "metta", "bodhi", "nirvana",
        ]:
            self._layers[name] = LayerStatus(name=name, active=False, version=__version__)

        logger.info("Samma Suit v%s initialized", __version__)

    def activate_sutra(self, settings=None) -> None:
        """Activate the SUTRA gateway layer (middleware)."""
        from samma.sutra.config import SUTRASettings
        from samma.sutra.middleware import SUTRAMiddleware

        settings = settings or SUTRASettings()
        self._sutra_middleware = SUTRAMiddleware(self.app, settings=settings)

        if self.app is not None:
            self.app.add_middleware(SUTRAMiddleware, settings=settings)

        self._layers["sutra"] = LayerStatus(
            name="sutra",
            active=True,
            version=__version__,
            detail=f"Gateway: {settings.rate_limit_per_ip} req/{settings.rate_limit_window_seconds}s per IP",
        )
        logger.info("SUTRA layer activated")

    def activate_dharma(self, settings=None, role_registry=None) -> None:
        """Activate the DHARMA permissions layer."""
        from samma.dharma.config import DHARMASettings
        from samma.dharma.policy import PolicyEngine
        from samma.dharma.roles import RoleRegistry
        from samma.dharma import dependencies

        settings = settings or DHARMASettings()
        role_registry = role_registry or RoleRegistry()

        self._policy_engine = PolicyEngine(
            role_registry=role_registry,
            settings=settings,
        )

        # Wire up the global dependency
        dependencies.set_policy_engine(self._policy_engine)
        dependencies.set_headers(settings.agent_header, settings.agent_type_header)

        self._layers["dharma"] = LayerStatus(
            name="dharma",
            active=True,
            version=__version__,
            detail=f"Permissions: {len(role_registry.list_roles())} roles, default-deny={settings.default_deny}",
        )
        logger.info("DHARMA layer activated")

    @property
    def policy_engine(self) -> Optional["PolicyEngine"]:
        return self._policy_engine

    def status(self) -> dict:
        """Return status of all Samma layers."""
        return {
            "samma_version": __version__,
            "layers": {
                name: layer.model_dump()
                for name, layer in self._layers.items()
            },
            "active_count": sum(1 for l in self._layers.values() if l.active),
            "total_layers": len(self._layers),
        }
