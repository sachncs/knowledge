"""Extension system for the knowledge SDK.

Extensions allow developers to customize parsing, extraction, verification,
repair, scoring, and serialization through a plugin mechanism based on
compiler passes. Plugins are discoverable through Python entry points.
"""

from __future__ import annotations

import importlib.metadata
from typing import Any

from knowledge.passes import CompilerPass, PassManager


class ExtensionConfig:
    """Configuration for enabling and disabling passes.

    Supports:
    - enabling specific passes
    - disabling specific passes
    - configuring pass-specific options
    - ordering passes
    """

    def __init__(
        self,
        enabled_passes: list[str] | None = None,
        disabled_passes: list[str] | None = None,
        pass_config: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Initialize an extension configuration.

        Args:
            enabled_passes: Only these pass IDs are allowed to run.
            disabled_passes: These pass IDs are explicitly excluded.
            pass_config: Pass-specific configuration keyed by pass ID.
        """
        self.enabled_passes = enabled_passes or []
        self.disabled_passes = disabled_passes or []
        self.pass_config = pass_config or {}

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> ExtensionConfig:
        """Create an ExtensionConfig from a dictionary.

        Args:
            config: Dictionary with optional keys ``enabled_passes``,
                ``disabled_passes``, and ``pass_config``.

        Returns:
            A new ExtensionConfig instance.
        """
        return cls(
            enabled_passes=config.get("enabled_passes", []),
            disabled_passes=config.get("disabled_passes", []),
            pass_config=config.get("pass_config", {}),
        )


class ExtensionRegistry:
    """Registry for discovering and managing extension passes.

    Extensions register themselves through Python entry points in the
    ``knowledge.passes`` group. Each entry point should resolve to a
    ``CompilerPass`` subclass.
    """

    ENTRY_POINT_GROUP = "knowledge.passes"

    def __init__(self) -> None:
        """Initialize an empty extension registry."""
        self.plugins: dict[str, type[CompilerPass]] = {}

    def discover(self) -> list[str]:
        """Discover plugins via Python entry points.

        Returns:
            List of discovered plugin pass IDs.
        """
        discovered: list[str] = []
        try:
            for ep in importlib.metadata.entry_points(group=self.ENTRY_POINT_GROUP):
                try:
                    pass_cls = ep.load()
                except (importlib.metadata.PackageNotFoundError, TypeError, AttributeError):
                    continue
                if isinstance(pass_cls, type) and issubclass(pass_cls, CompilerPass):
                    instance = pass_cls()
                    self.plugins[instance.id] = pass_cls
                    discovered.append(instance.id)
        except importlib.metadata.PackageNotFoundError:
            pass
        return discovered

    def register_plugin(self, pass_cls: type[CompilerPass]) -> str:
        """Register a plugin pass class.

        Args:
            pass_cls: A CompilerPass subclass to register.

        Returns:
            The pass ID of the registered plugin.
        """
        instance = pass_cls()
        self.plugins[instance.id] = pass_cls
        return instance.id

    def apply_to(
        self,
        pass_manager: PassManager,
        config: ExtensionConfig | None = None,
    ) -> list[str]:
        """Apply discovered and enabled plugins to a PassManager.

        Args:
            pass_manager: The PassManager to register passes with.
            config: Optional configuration for enabling/disabling passes.

        Returns:
            List of registered pass IDs.
        """
        registered: list[str] = []
        cfg = config or ExtensionConfig()
        enabled_set = set(cfg.enabled_passes)
        disabled_set = set(cfg.disabled_passes)

        for pid, pass_cls in self.plugins.items():
            if cfg.enabled_passes and pid not in enabled_set:
                continue
            if pid in disabled_set:
                continue
            try:
                instance = pass_cls()
                pass_manager.register(instance)
                registered.append(pid)
            except ValueError:
                pass

        return registered
