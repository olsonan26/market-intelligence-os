"""Sealed as-of snapshots: reproducible, stable under later ingestion (Laws 1, 11)."""
from __future__ import annotations

import json
from typing import List, Optional

from ..contracts.hashing import canonical_json, sha256_hex
from ..pipeline.replay import order_key
from ..storage.event_store import EventStore
from .visibility import VisibilityPolicy, decide_visibility


def build_snapshot(store: EventStore, cutoff_utc: str, policy: VisibilityPolicy) -> dict:
    """A sealed snapshot: the ordered visible versions + decisions + a content hash."""
    decisions = decide_visibility(store, cutoff_utc, policy)
    visible_keys = {(d.event_id, d.version) for d in decisions if d.visible}
    retracted_keys = {(d.event_id, d.version) for d in decisions if d.visible and d.retracted_by_visible_retraction}
    rows = [r for r in store.all_events() if (r["event_id"], r["version"]) in visible_keys]
    ordered = sorted(rows, key=order_key)
    events = [
        {
            "event_id": r["event_id"], "version": r["version"], "version_kind": r["version_kind"],
            "event_time": r["event_time_utc"], "published_at": r["published_at_utc"],
            "ingested_at": r["ingested_at_utc"], "payload": json.loads(r["payload_json"]),
            "raw_sha256": r["raw_sha256"],
            "marked_retracted": (r["event_id"], r["version"]) in retracted_keys,
        }
        for r in ordered
    ]
    body = {
        "cutoff": cutoff_utc,
        "policy": policy.value,
        "events": events,
        "decisions": [d.to_canonical_dict() for d in decisions],
    }
    return {**body, "snapshot_hash": sha256_hex(canonical_json({"cutoff": cutoff_utc, "policy": policy.value, "events": events}))}


def explain_event(store: EventStore, cutoff_utc: str, policy: VisibilityPolicy, event_id: str) -> List[dict]:
    return [d.to_canonical_dict() for d in decide_visibility(store, cutoff_utc, policy) if d.event_id == event_id]
