"""External engine adapters: contract-only, entitlement pending (never fabricate)."""
from __future__ import annotations

from .engine_port import EntitlementPending


class NautilusTraderEngine:
    name = "nautilus_trader"
    state = "ENTITLEMENT_PENDING"

    def __init__(self) -> None:
        raise EntitlementPending(
            "NautilusTrader is not installed in this environment. Provide an environment with"
            " 'pip install nautilus_trader' to run the SIM-008 bake-off."
        )


class LeanEngine:
    name = "lean"
    state = "ENTITLEMENT_PENDING"

    def __init__(self) -> None:
        raise EntitlementPending(
            "QuantConnect LEAN requires the dotnet runtime and LEAN CLI. Provide them to run the"
            " SIM-008 bake-off."
        )
