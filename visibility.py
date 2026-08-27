"""Visibility policies for point-in-time reconstruction (Law 1).

Two governing questions the spec distinguishes:
- PUBLIC_KNOWABLE: what was publicly knowable at the cutoff (governing clock: published_at,
  falling back to ingested_at when a source has no publication clock).
- SYSTEM_RECEIVED: what THIS system had genuinely received at the cutoff (governing clock: ingested_at).

Retractions: a retraction version visible at cutoff makes prior versions of that event
visible-as-retracted (never silently deleted). Corrections/revisions: each version is judged
independently; later versions never leak before their own visibility time.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ..storage.event_store import EventStore


class VisibilityPolicy(Enum):
    PUBLIC_KNOWABLE = "public_knowable"
    SYSTEM_RECEIVED = "system_received"


GOVERNING_SQL = {
    VisibilityPolicy.PUBLIC_KNOWABLE: "COALESCE(published_at_utc, ingested_at_utc)",
    VisibilityPolicy.SYSTEM_RECEIVED: "ingested_at_utc",
}


@dataclass(frozen=True)
class VisibilityDecision:
    event_id: str
    version: int
    visible: bool
    governing_clock: str
    governing_value: Optional[str]
    policy: str
    cutoff: str
    reason: str
    retracted_by_visible_retraction: bool = False

    def to_canonical_dict(self) -> dict:
        return {
            "event_id": self.event_id, "version": self.version, "visible": self.visible,
            "governing_clock": self.governing_clock, "governing_value": self.governing_value,
            "policy": self.policy, "cutoff": self.cutoff, "reason": self.reason,
            "retracted_by_visible_retraction": self.retracted_by_visible_retraction,
        }


def governing_value(row, policy: VisibilityPolicy) -> Optional[str]:
    if policy is VisibilityPolicy.SYSTEM_RECEIVED:
        return row["ingested_at_utc"]
    return row["published_at_utc"] or row["ingested_at_utc"]


def governing_clock_name(row, policy: VisibilityPolicy) -> str:
    if policy is VisibilityPolicy.SYSTEM_RECEIVED:
        return "ingested_at"
    return "published_at" if row["published_at_utc"] else "ingested_at(fallback)"


def decide_visibility(store: EventStore, cutoff_utc: str, policy: VisibilityPolicy) -> List[VisibilityDecision]:
    """Explain, for EVERY stored version, why it is visible or invisible at the cutoff."""
    rows = store.all_events()
    # first pass: which retraction versions are themselves visible at cutoff
    visible_retractions: Dict[str, int] = {}
    for r in rows:
        gv = governing_value(r, policy)
        if r["version_kind"] == "retraction" and gv is not None and gv <= cutoff_utc:
            visible_retractions[r["event_id"]] = r["version"]

    decisions: List[VisibilityDecision] = []
    for r in rows:
        gv = governing_value(r, policy)
        clock = governing_clock_name(r, policy)
        visible = gv is not None and gv <= cutoff_utc
        if visible:
            retracted = r["event_id"] in visible_retractions and r["version"] < visible_retractions[r["event_id"]]
            reason = (
                f"{clock}={gv} <= cutoff {cutoff_utc} under policy {policy.value}"
                + ("; a later retraction is also visible, version is marked retracted" if retracted else "")
            )
            decisions.append(VisibilityDecision(r["event_id"], r["version"], True, clock, gv,
                                                policy.value, cutoff_utc, reason, retracted))
        else:
            reason = f"{clock}={gv} > cutoff {cutoff_utc} under policy {policy.value}: knowledge did not exist yet"
            decisions.append(VisibilityDecision(r["event_id"], r["version"], False, clock, gv,
                                                policy.value, cutoff_utc, reason, False))
    return decisions
