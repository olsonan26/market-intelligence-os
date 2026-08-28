"""Deterministic reference simulation engine.

Fully deterministic: same ordered events + strategy + frictions + latency + checkpoint
=> identical orders, fills, P&L, and hashes (SIM-002). Supports latency and partial
fills (SIM-003), full friction accounting (SIM-004), knowledge-time enforcement for
custom events (SIM-006), and checkpoint/restart equivalence (SIM-007).
"""
from __future__ import annotations

import json
from decimal import Decimal
from typing import List, Mapping, Optional, Sequence

from ..contracts.hashing import canonical_json, sha256_hex
from .engine_port import FrictionModel, LatencyModel, SimFill, SimOrder


class DeterministicSimEngine:
    name = "reference-deterministic"

    def run(self, events: Sequence[Mapping], strategy, frictions: FrictionModel,
            latency: LatencyModel, checkpoint: Optional[dict] = None) -> dict:
        state = {
            "cash": Decimal(checkpoint["cash"]) if checkpoint else Decimal("100000"),
            "position": Decimal(checkpoint["position"]) if checkpoint else Decimal("0"),
            "pending": list(checkpoint["pending"]) if checkpoint else [],
            "start_index": int(checkpoint["next_index"]) if checkpoint else 0,
        }
        orders: List[dict] = list(checkpoint["orders"]) if checkpoint else []
        fills: List[dict] = list(checkpoint["fills"]) if checkpoint else []
        knowledge_violations: List[dict] = []

        for i in range(state["start_index"], len(events)):
            ev = events[i]
            # SIM-006: custom events must not act before their knowledge time
            visible_at = ev.get("visible_at_index", i)
            if visible_at > i:
                knowledge_violations.append({"index": i, "reason": "event not knowable yet"})
                continue
            price = Decimal(str(ev["payload"]["price"]))

            # execute pending orders whose latency elapsed
            still_pending = []
            for p in state["pending"]:
                if i - p["submitted_at_index"] >= latency.order_latency_events:
                    qty = Decimal(p["quantity"])
                    fill_qty = (qty * latency.partial_fill_fraction).quantize(Decimal("0.0001")) if p.get("constrained") else qty
                    exec_price = price + (frictions.spread / 2 + frictions.slippage_per_unit) * (1 if p["side"] == "buy" else -1)
                    commission = (frictions.commission_per_unit * fill_qty).quantize(Decimal("0.0001"))
                    signed = fill_qty if p["side"] == "buy" else -fill_qty
                    state["position"] += signed
                    state["cash"] -= signed * exec_price + commission
                    fills.append({
                        "order_id": p["order_id"], "quantity": str(fill_qty), "price": str(exec_price),
                        "at_index": i, "commission": str(commission),
                        "slippage": str(frictions.slippage_per_unit), "partial": bool(p.get("constrained")),
                    })
                    if p.get("constrained") and fill_qty < qty:
                        rest = dict(p); rest["quantity"] = str(qty - fill_qty); rest["constrained"] = False
                        rest["submitted_at_index"] = i
                        still_pending.append(rest)
                else:
                    still_pending.append(p)
            state["pending"] = still_pending

            # strategy decision (pure function of event + position)
            action = strategy(ev, state["position"])
            if action is not None:
                order = {
                    "order_id": f"o-{len(orders)+1:04d}", "instrument_id": ev["payload"].get("symbol", "FIXTURE-XYZ"),
                    "side": action["side"], "quantity": str(Decimal(str(action["quantity"]))),
                    "submitted_at_index": i, "constrained": bool(action.get("constrained")),
                }
                orders.append(order)
                state["pending"].append(dict(order))

            # daily funding on held position (per event tick as fixture convention)
            state["cash"] -= abs(state["position"]) * price * frictions.funding_rate_daily

        last_price = Decimal(str(events[-1]["payload"]["price"])) if events else Decimal("0")
        equity = state["cash"] + state["position"] * last_price
        result = {
            "engine": self.name,
            "orders": orders, "fills": fills,
            "final_cash": str(state["cash"].quantize(Decimal("0.0001"))),
            "final_position": str(state["position"]),
            "equity": str(equity.quantize(Decimal("0.0001"))),
            "knowledge_violations": knowledge_violations,
            "checkpoint": {
                "cash": str(state["cash"]), "position": str(state["position"]),
                "pending": state["pending"], "orders": orders, "fills": fills,
                "next_index": len(events),
            },
        }
        hashable = {k: result[k] for k in ("engine", "orders", "fills", "final_cash", "final_position", "equity")}
        result["result_hash"] = sha256_hex(canonical_json(hashable))
        return result
