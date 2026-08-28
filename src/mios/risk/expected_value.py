"""Net expected value with every configured friction (EV-001/002)."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict


@dataclass(frozen=True)
class FrictionConfig:
    spread: Decimal
    fees: Decimal
    slippage: Decimal
    funding: Decimal
    latency_cost: Decimal
    partial_fill_cost: Decimal
    margin_cost: Decimal
    market_impact: Decimal

    def total(self) -> Decimal:
        return (self.spread + self.fees + self.slippage + self.funding + self.latency_cost
                + self.partial_fill_cost + self.margin_cost + self.market_impact)

    def to_canonical_dict(self) -> dict:
        return {k: str(getattr(self, k)) for k in
                ("spread", "fees", "slippage", "funding", "latency_cost",
                 "partial_fill_cost", "margin_cost", "market_impact")}


def net_expected_value(p_win: Decimal, win_amount: Decimal, loss_amount: Decimal,
                       frictions: FrictionConfig) -> dict:
    raw_ev = p_win * win_amount - (Decimal("1") - p_win) * loss_amount
    net_ev = raw_ev - frictions.total()
    return {"raw_ev": str(raw_ev.quantize(Decimal("0.0001"))),
            "net_ev": str(net_ev.quantize(Decimal("0.0001"))),
            "frictions": frictions.to_canonical_dict(),
            "friction_total": str(frictions.total())}
