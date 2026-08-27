"""Deterministic replay with the spec's total order (Law 11).

The replay hash covers knowledge-relevant fields only (identity, clocks other than
system_time, payload, raw hash). system_time is an operational clock; including it
would make replay identity depend on when the machine ran, violating Law 11.
"""
from __future__ import annotations

import json
from typing import List

from ..contracts.hashing import canonical_json, sha256_hex
from ..storage.event_store import EventStore

# Total order (spec section 10):
# governing visibility time -> source sequence -> event time -> source id -> source event id -> raw hash
def order_key(row) -> tuple:
    return (
        row["ingested_at_utc"],
        row["source_sequence"] if row["source_sequence"] is not None else -1,
        row["event_time_utc"],
        row["source_id"],
        row["source_event_id"] or "",
        row["raw_sha256"],
    )


def replay(store: EventStore, cutoff_utc: str | None = None,
           governing_clock: str = "ingested_at_utc") -> dict:
    rows = (store.events_visible_at(cutoff_utc, governing_clock) if cutoff_utc
            else store.all_events())
    ordered = sorted(rows, key=order_key)
    events = [
        {
            "event_id": r["event_id"], "version": r["version"], "version_kind": r["version_kind"],
            "event_time": r["event_time_utc"], "published_at": r["published_at_utc"],
            "ingested_at": r["ingested_at_utc"], "payload": json.loads(r["payload_json"]),
            "raw_sha256": r["raw_sha256"],
        }
        for r in ordered
    ]
    body = canonical_json(events)
    return {"events": events, "count": len(events), "replay_hash": sha256_hex(body)}
