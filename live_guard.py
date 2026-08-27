"""LIVE-000: no live-capital route exists or can be enabled by configuration alone."""
from __future__ import annotations

from typing import Mapping


class LiveAuthorityConfigError(PermissionError):
    """A configuration attempted to enable live trading. This is constitutionally impossible."""


FORBIDDEN_CONFIG_KEYS = ("live_trading", "enable_live", "live_orders", "production_orders", "real_money")


def validate_runtime_config(config: Mapping) -> Mapping:
    """Any configuration that even names a live-trading flag is rejected outright."""
    for key in config:
        lowered = str(key).lower()
        for forbidden in FORBIDDEN_CONFIG_KEYS:
            if forbidden in lowered:
                raise LiveAuthorityConfigError(
                    f"configuration key '{key}' attempts to reference live authority; "
                    "live capital requires a separate written authorization outside this codebase")
    return config
