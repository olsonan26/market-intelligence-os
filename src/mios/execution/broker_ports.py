"""Broker adapter ports: contract-defined, entitlement pending. NO SDK imports (law 14)."""
from __future__ import annotations

from ..simulation.engine_port import EntitlementPending

BROKER_STATES = {
    "IBKR": "ENTITLEMENT_PENDING",
    "OANDA_V20": "ENTITLEMENT_PENDING",
    "KRAKEN": "ENTITLEMENT_PENDING",
    "TRADOVATE": "NOT_STARTED",
    "ALPACA": "NOT_STARTED",
    "MT5": "NOT_STARTED",
    "COINBASE": "NOT_STARTED",
}


class SandboxBrokerPort:
    """Typed port for future paper/sandbox adapters. Instantiating any external venue raises
    until Alex provides sandbox credentials — fixture verification is never upgraded silently."""

    def __init__(self, venue: str) -> None:
        state = BROKER_STATES.get(venue, "NOT_STARTED")
        raise EntitlementPending(
            f"{venue} sandbox adapter is {state}: requires a paper/sandbox account and credentials"
            f" provided by Alex through the secure runtime environment (never committed)."
        )
