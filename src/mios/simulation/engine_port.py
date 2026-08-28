"""Framework-neutral SimulationEngine contract (Phase 3)."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Mapping, Optional, Protocol, Sequence, Tuple


class EntitlementPending(RuntimeError):
    """External engine not installed/verified; fixture verification cannot be upgraded."""


@dataclass(frozen=True)
class FrictionModel:
    commission_per_unit: Decimal = Decimal("0.005")
    spread: Decimal = Decimal("0.02")
    slippage_per_unit: Decimal = Decimal("0.01")
    funding_rate_daily: Decimal = Decimal("0.0001")
    margin_requirement: Decimal = Decimal("0.5")

    def to_canonical_dict(self) -> dict:
        return {
            "commission_per_unit": str(self.commission_per_unit), "spread": str(self.spread),
            "slippage_per_unit": str(self.slippage_per_unit),
            "funding_rate_daily": str(self.funding_rate_daily),
            "margin_requirement": str(self.margin_requirement),
        }


@dataclass(frozen=True)
class LatencyModel:
    order_latency_events: int = 1      # orders act N events after submission
    partial_fill_fraction: Decimal = Decimal("0.5")  # first fill fraction when liquidity constrained


@dataclass(frozen=True)
class SimOrder:
    order_id: str
    instrument_id: str
    side: str            # buy | sell
    quantity: Decimal
    submitted_at_index: int


@dataclass(frozen=True)
class SimFill:
    order_id: str
    quantity: Decimal
    price: Decimal
    at_index: int
    commission: Decimal
    slippage: Decimal
    partial: bool


class SimulationEngine(Protocol):
    """Any engine (reference, NautilusTrader, LEAN) implements exactly this."""

    def run(self, events: Sequence[Mapping], strategy, frictions: FrictionModel,
            latency: LatencyModel, checkpoint: Optional[dict] = None) -> dict:
        ...
