"""Versioned point-in-time feature sets (Phase 4). Every value traces to permitted inputs (VAL-008)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..contracts.hashing import canonical_json, sha256_hex
from ..storage.event_store import EventStore
from ..timemachine.snapshot import build_snapshot
from ..timemachine.visibility import VisibilityPolicy


class FutureLeakError(ValueError):
    """A feature attempted to read knowledge past its cutoff (VAL-001)."""


@dataclass(frozen=True)
class FeatureValue:
    name: str
    value: str
    as_of: str
    input_event_versions: Tuple[Tuple[str, int], ...]  # provenance (VAL-008)


class PointInTimeFeatureBuilder:
    """Features may ONLY read from a sealed as-of snapshot; the raw store is not reachable."""

    def __init__(self, store: EventStore, cutoff_utc: str,
                 policy: VisibilityPolicy = VisibilityPolicy.SYSTEM_RECEIVED) -> None:
        self._cutoff = cutoff_utc
        snap = build_snapshot(store, cutoff_utc, policy)
        self._events = snap["events"]
        self._snapshot_hash = snap["snapshot_hash"]

    def declare_input(self, event_time: str) -> None:
        if event_time > self._cutoff:
            raise FutureLeakError(f"feature input at {event_time} exceeds cutoff {self._cutoff}")

    def mean_price(self, last_n: int) -> FeatureValue:
        rows = [e for e in self._events
                if e["payload"].get("price") is not None or e["payload"].get("value") is not None][-last_n:]
        for e in rows:
            self.declare_input(e["ingested_at"])
        if not rows:
            return FeatureValue("mean_price", "NaN", self._cutoff, tuple())
        total = sum(float(e["payload"].get("price") or e["payload"]["value"]) for e in rows)
        return FeatureValue(
            "mean_price", f"{total/len(rows):.4f}", self._cutoff,
            tuple((e["event_id"], e["version"]) for e in rows),
        )

    def feature_set(self, last_n: int = 3) -> dict:
        f = self.mean_price(last_n)
        body = {
            "features": [{"name": f.name, "value": f.value, "as_of": f.as_of,
                          "inputs": list(map(list, f.input_event_versions))}],
            "cutoff": self._cutoff, "snapshot_hash": self._snapshot_hash,
        }
        return {**body, "feature_set_hash": sha256_hex(canonical_json(body)), "version": "1.0.0"}
