"""Real-time shadow operation with ZERO order authority (Phase 9).

SH-001: zero order authority is structurally enforced — the shadow runner has no broker
reference, no submit method, and records a would-be decision only.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Sequence


class OrderAuthorityViolation(PermissionError):
    """Something attempted to give the shadow path order authority."""


@dataclass(frozen=True)
class ShadowDecision:
    decision_id: str
    at_index: int
    would_action: str            # "would_enter" | "would_exit" | "no_trade"
    reasons: tuple
    evidence_roots: tuple
    input_event_ids: tuple
    lineage_hash: str


class ShadowRunner:
    """Consumes canonical events, produces decisions, cannot hold or receive a broker."""

    __slots__ = ("_decisions", "_seen_event_ids", "_max_staleness")

    def __init__(self, max_staleness_indices: int = 3) -> None:
        self._decisions: List[ShadowDecision] = []
        self._seen_event_ids: set = set()
        self._max_staleness = max_staleness_indices

    def __setattr__(self, name, value):
        if name in ("broker", "order_router", "submit_order", "paper_broker"):
            raise OrderAuthorityViolation("shadow mode may never hold order authority (SH-001)")
        object.__setattr__(self, name, value)

    def run(self, events: Sequence[dict], strategy, start_index: int = 0) -> List[ShadowDecision]:
        last_data_index = start_index - 1
        for i in range(start_index, len(events)):
            ev = events[i]
            eid = ev.get("event_id", f"idx-{i}")
            if eid in self._seen_event_ids:
                continue  # SH-004: duplicate-event recovery, no duplicate decisions
            self._seen_event_ids.add(eid)
            if ev.get("is_data", True):
                last_data_index = i
            staleness = i - last_data_index
            if staleness > self._max_staleness:
                action, reasons = "no_trade", (f"stale data: {staleness} indices without fresh data (SH-003)",)
            else:
                proposed = strategy(ev)
                action = proposed if proposed in ("would_enter", "would_exit") else "no_trade"
                reasons = (f"strategy proposed {proposed}",)
            roots = tuple(ev.get("evidence_roots", ()))
            lineage = {"decision_inputs": [eid], "roots": list(roots), "action": action}
            digest = hashlib.sha256(json.dumps(lineage, sort_keys=True).encode()).hexdigest()
            self._decisions.append(ShadowDecision(
                decision_id=f"sd-{len(self._decisions)+1:05d}", at_index=i, would_action=action,
                reasons=reasons, evidence_roots=roots, input_event_ids=(eid,), lineage_hash=digest))
        return list(self._decisions)

    def decisions(self) -> List[ShadowDecision]:
        return list(self._decisions)
