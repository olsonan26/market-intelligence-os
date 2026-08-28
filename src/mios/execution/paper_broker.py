"""Paper execution: venue-neutral TradeIntents -> capability-checked paper orders (Phase 8).

NO live authority: this module simulates a paper venue only. Broker adapters for IBKR/OANDA/Kraken
are ports with ENTITLEMENT_PENDING state (see broker_ports.py) — no SDK imports exist anywhere.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class VenueCapabilities:
    venue_id: str
    supports_oco: bool
    supports_market: bool = True
    supports_limit: bool = True


class CapabilityError(RuntimeError):
    """The venue cannot natively express the requested order feature (EX-002: no silent emulation)."""


@dataclass(frozen=True)
class TradeIntent:
    intent_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    order_type: str = "market"
    requires_oco: bool = False


class PaperLedger:
    """Append-only order/fill/position ledger; state is always reconstructable (EX-001)."""

    def __init__(self) -> None:
        self.entries: List[dict] = []

    def append(self, kind: str, data: dict) -> None:
        self.entries.append({"seq": len(self.entries) + 1, "kind": kind, **data})

    def reconstruct(self) -> dict:
        """Deterministic fold over the append-only ledger."""
        orders: Dict[str, dict] = {}
        position = Decimal("0")
        for e in self.entries:
            if e["kind"] == "order_accepted":
                orders[e["order_id"]] = {"remaining": Decimal(e["quantity"]), "status": "open",
                                         "side": e["side"]}
            elif e["kind"] == "fill":
                o = orders[e["order_id"]]
                qty = Decimal(e["quantity"])
                o["remaining"] -= qty
                position += qty if o["side"] == "buy" else -qty
                if o["remaining"] <= 0:
                    o["status"] = "filled"
                else:
                    o["status"] = "partially_filled"
            elif e["kind"] == "order_cancelled":
                orders[e["order_id"]]["status"] = "cancelled"
        state = {"orders": {k: {"remaining": str(v["remaining"]), "status": v["status"], "side": v["side"]}
                            for k, v in orders.items()},
                 "position": str(position)}
        state["state_hash"] = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        return state


class PaperBroker:
    """Idempotent, capability-checked paper venue (EX-002/003)."""

    def __init__(self, capabilities: VenueCapabilities, ledger: PaperLedger) -> None:
        self._caps = capabilities
        self._ledger = ledger
        self._idempotency: Dict[str, str] = {}
        self._order_count = 0

    def submit_paper_order(self, intent: TradeIntent, idempotency_key: str) -> str:
        if intent.requires_oco and not self._caps.supports_oco:
            raise CapabilityError(
                f"venue {self._caps.venue_id} does not support native OCO; refusing silent emulation (EX-002)")
        if idempotency_key in self._idempotency:
            return self._idempotency[idempotency_key]      # EX-003: no duplicate order
        self._order_count += 1
        order_id = f"paper-{self._order_count:05d}"
        self._idempotency[idempotency_key] = order_id
        self._ledger.append("order_accepted", {"order_id": order_id, "intent_id": intent.intent_id,
                                               "side": intent.side, "quantity": str(intent.quantity),
                                               "venue": self._caps.venue_id, "mode": "PAPER"})
        return order_id

    def fill(self, order_id: str, quantity: Decimal, price: Decimal) -> None:
        self._ledger.append("fill", {"order_id": order_id, "quantity": str(quantity), "price": str(price)})


def reconcile(ledger_state: dict, venue_snapshot: dict) -> dict:
    """Continuous reconciliation between internal ledger and venue snapshot (law 13, EX-004)."""
    mismatches = []
    if ledger_state["position"] != venue_snapshot.get("position"):
        mismatches.append({"field": "position", "ledger": ledger_state["position"],
                           "venue": venue_snapshot.get("position")})
    for oid, o in ledger_state["orders"].items():
        v = venue_snapshot.get("orders", {}).get(oid)
        if v is None:
            if o["status"] in ("open", "partially_filled"):
                mismatches.append({"field": f"order:{oid}", "ledger": o["status"], "venue": "missing"})
        elif v["status"] != o["status"] or v.get("remaining") != o["remaining"]:
            mismatches.append({"field": f"order:{oid}", "ledger": o, "venue": v})
    return {"reconciled": not mismatches, "mismatches": mismatches}
