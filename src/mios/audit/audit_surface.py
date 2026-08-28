"""Auditable operator surface (Phase 10) — canonical read-only projection.

UI-001: every displayed metric deep-links to canonical lineage.
UI-002: the display layer cannot alter canonical calculations (read-only projections).
UI-003: role restrictions block unauthorized approvals/risk controls.
UI-004: fixture/shadow/paper/real source states cannot be visually confused (mandatory badges).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional

SOURCE_BADGES = {"fixture": "FIXTURE", "shadow": "SHADOW", "paper": "PAPER", "real": "REAL"}
ROLES = {"viewer": set(), "operator": {"approve_queue"}, "risk_officer": {"approve_queue", "kill_switch"}}


class RoleError(PermissionError):
    """Role lacks the attempted control action."""


@dataclass(frozen=True)
class DisplayMetric:
    metric_id: str
    label: str
    value: str
    source_state: str                 # fixture | shadow | paper | real
    lineage: Mapping[str, Any]        # event ids, versions, snapshot hash, policy ids

    def render(self) -> dict:
        if self.source_state not in SOURCE_BADGES:
            raise ValueError("unknown source state")
        if not self.lineage.get("event_versions") and not self.lineage.get("decision_id"):
            raise ValueError("metric refuses to render without lineage (UI-001)")
        return {
            "badge": SOURCE_BADGES[self.source_state],   # mandatory, non-optional badge (UI-004)
            "label": f"[{SOURCE_BADGES[self.source_state]}] {self.label}",
            "value": self.value,
            "deep_link": {"lineage": dict(self.lineage)},
        }


class AuditSurface:
    """Read-only projection over canonical results; mutation is structurally impossible (UI-002)."""

    def __init__(self, canonical_results: Dict[str, Any]) -> None:
        frozen = json.loads(json.dumps(canonical_results, sort_keys=True))
        self._canonical = MappingProxyType(frozen)
        self._canonical_hash = hashlib.sha256(
            json.dumps(frozen, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    @property
    def canonical(self) -> Mapping[str, Any]:
        return self._canonical

    def canonical_hash(self) -> str:
        return self._canonical_hash

    def act(self, role: str, action: str) -> str:
        allowed = ROLES.get(role, set())
        if action not in allowed:
            raise RoleError(f"role '{role}' may not perform '{action}' (UI-003)")
        return f"{action}:permitted"
