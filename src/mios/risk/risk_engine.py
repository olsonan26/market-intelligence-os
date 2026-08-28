"""Deterministic risk engine: freshness, concentration, margin, kill switches, no-trade (Phase 7).

Risk decisions are deterministic and reproducible (law 9); independent from LLM output (law 8);
no-trade is a first-class action (law 10).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class RiskPolicy:
    policy_id: str
    max_staleness_seconds: int
    max_correlated_exposure: Decimal      # combined exposure cap for one correlation group
    margin_usage_limit: Decimal           # fraction of margin capacity
    version: str = "1.0.0"

    def to_canonical_dict(self) -> dict:
        return {"policy_id": self.policy_id, "max_staleness_seconds": self.max_staleness_seconds,
                "max_correlated_exposure": str(self.max_correlated_exposure),
                "margin_usage_limit": str(self.margin_usage_limit), "version": self.version}


@dataclass(frozen=True)
class TradeIntentRequest:
    intent_id: str
    instrument_id: str
    side: str
    quantity: Decimal
    correlation_group: str
    is_risk_reducing: bool = False


@dataclass
class RiskState:
    data_age_seconds: int
    exposures_by_group: Dict[str, Decimal]
    margin_used: Decimal
    margin_capacity: Decimal
    kill_switches: Dict[str, bool] = field(default_factory=dict)   # global/venue/strategy/instrument


@dataclass(frozen=True)
class RiskDecision:
    intent_id: str
    action: str          # "approve" | "no_trade"
    reasons: Tuple[str, ...]
    policy_id: str
    decision_hash: str


class KillSwitchRegistry:
    """Deterministic, authenticated, logged kill switches (RS-004)."""

    def __init__(self, authorized_operators: Tuple[str, ...]) -> None:
        self._authorized = set(authorized_operators)
        self._states: Dict[str, bool] = {"global": False}
        self._log: List[dict] = []

    def set(self, scope: str, engaged: bool, operator: str) -> None:
        if operator not in self._authorized:
            raise PermissionError(f"operator '{operator}' is not authorized for kill switches")
        self._states[scope] = engaged
        self._log.append({"scope": scope, "engaged": engaged, "operator": operator, "seq": len(self._log) + 1})

    def engaged(self, scope: str) -> bool:
        return self._states.get("global", False) or self._states.get(scope, False)

    def log(self) -> List[dict]:
        return list(self._log)


def decide(req: TradeIntentRequest, state: RiskState, policy: RiskPolicy,
           kills: Optional[KillSwitchRegistry] = None) -> RiskDecision:
    reasons: List[str] = []

    if kills is not None and (kills.engaged("global") or kills.engaged(req.instrument_id)
                              or kills.engaged(req.correlation_group)):
        reasons.append("kill switch engaged")

    if state.data_age_seconds > policy.max_staleness_seconds:
        if req.is_risk_reducing:
            pass  # RS-001: risk-reducing actions remain possible on stale data
        else:
            reasons.append(f"stale data: {state.data_age_seconds}s > {policy.max_staleness_seconds}s; new entries blocked")

    group_exposure = state.exposures_by_group.get(req.correlation_group, Decimal("0"))
    if not req.is_risk_reducing and group_exposure + req.quantity > policy.max_correlated_exposure:
        reasons.append(
            f"correlated exposure {group_exposure}+{req.quantity} exceeds group cap {policy.max_correlated_exposure} (RS-002)")

    projected_margin = state.margin_used + req.quantity
    if not req.is_risk_reducing and projected_margin > state.margin_capacity * policy.margin_usage_limit:
        reasons.append("margin/liquidation threshold breach (RS-003)")

    action = "no_trade" if reasons else "approve"
    basis = {"intent": req.intent_id, "action": action, "reasons": reasons,
             "policy": policy.to_canonical_dict()}
    digest = hashlib.sha256(json.dumps(basis, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return RiskDecision(req.intent_id, action, tuple(reasons), policy.policy_id, digest)


def gate_trade_intent(calibrated: dict, net_ev: dict, decision: RiskDecision) -> dict:
    """NT-001: inadequate evidence/calibration or negative net EV or risk breach => abstention, no TradeIntent."""
    if calibrated.get("abstain"):
        return {"trade_intent": None, "action": "no_trade", "reason": "calibration evidence insufficient (NT-001)"}
    if Decimal(net_ev["net_ev"]) <= 0:
        return {"trade_intent": None, "action": "no_trade", "reason": "net expected value non-positive (EV-002)"}
    if decision.action != "approve":
        return {"trade_intent": None, "action": "no_trade", "reason": "; ".join(decision.reasons)}
    return {"trade_intent": {"intent_id": decision.intent_id, "venue_neutral": True}, "action": "approve",
            "reason": "all gates passed"}
