"""Adversarial bitemporal fixtures for the Time Machine acceptance suite.

All records are labeled fixtures (impossible to confuse with real market data).
The scenario deliberately contains: revision, correction, retraction, late arrival,
archive backfill (published long before genuinely ingested), and interleaved sources.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from ..adapters.port import RawCapture
from ..contracts.clocks import DeterministicClock, FourClocks
from ..contracts.events import CanonicalEvent, SourceRef
from ..contracts.hashing import sha256_hex
from ..contracts.instruments import InstrumentRef
from ..contracts.licensing import LicensePolicy
from ..contracts.timestamps import PointInTimeTimestamp, TimePrecision
from ..storage.event_store import EventStore

BASE = datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
INSTR = InstrumentRef(instrument_id="FIX-XYZ", symbol="FIXTURE-XYZ", venue="FIXTURE", asset_class="equity")
POLICY = LicensePolicy(license_id="FIXTURE-LICENSE-INTERNAL-ONLY", internal_research=True, derived_signals=True)


def _ts(dt: datetime, raw: str | None = None) -> PointInTimeTimestamp:
    return PointInTimeTimestamp(utc=dt, precision=TimePrecision.SECOND, raw_text=raw, source_timezone="UTC")


def _mk(store: EventStore, event_id: str, version: int, kind: str, seq: int,
        event_t: datetime, pub_t: datetime | None, ing_t: datetime, sys_t: datetime, payload: dict) -> None:
    payload = {"fixture": True, "banner": "FIXTURE-TEST-DATA-NOT-REAL-MARKET-DATA", **payload}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    raw_hash = sha256_hex(raw)
    cap = RawCapture(source_id="FIXTURE-NEWS-V1", provider="fixture", raw_bytes=raw,
                     received_at=_ts(ing_t), content_type="application/json",
                     source_sequence=seq, is_test_fixture=True)
    store.store_raw(cap, raw_hash, sys_t.isoformat())
    event = CanonicalEvent(
        event_id=event_id, schema_name="mios.canonical_event", schema_version="1.0.0",
        source=SourceRef(source_id="FIXTURE-NEWS-V1", provider="fixture",
                         source_event_id=f"{event_id}-v{version}", source_sequence=seq),
        clocks=FourClocks(event_time=_ts(event_t), published_at=_ts(pub_t) if pub_t else None,
                          ingested_at=_ts(ing_t), system_time=_ts(sys_t)),
        payload=payload, raw_payload_sha256=raw_hash, license_policy=POLICY,
        evidence_roots=(raw_hash,), instrument=INSTR, is_test_fixture=True)
    store.append_event(event, version=version, version_kind=kind)


def build_adversarial_store() -> EventStore:
    store = EventStore(":memory:")
    H = timedelta(hours=1)
    # evt-A: original at 12:00 published/ingested 12:05; revision published 14:00; correction published 16:00
    _mk(store, "evt-A", 1, "original", 1, BASE, BASE + timedelta(minutes=5), BASE + timedelta(minutes=6), BASE + 9 * H, {"headline": "initial report", "value": "10"})
    _mk(store, "evt-A", 2, "revision", 2, BASE, BASE + 2 * H, BASE + 2 * H + timedelta(minutes=1), BASE + 9 * H, {"headline": "revised report", "value": "12"})
    _mk(store, "evt-A", 3, "correction", 3, BASE, BASE + 4 * H, BASE + 4 * H + timedelta(minutes=1), BASE + 9 * H, {"headline": "corrected report", "value": "11"})
    # evt-B: original then RETRACTION published 15:00
    _mk(store, "evt-B", 1, "original", 4, BASE + H, BASE + H, BASE + H + timedelta(minutes=2), BASE + 9 * H, {"headline": "story B", "value": "77"})
    _mk(store, "evt-B", 2, "retraction", 5, BASE + H, BASE + 3 * H, BASE + 3 * H + timedelta(minutes=2), BASE + 9 * H, {"headline": "story B retracted", "value": None})
    # evt-C: LATE ARRIVAL — happened & published 12:30 but system only ingested at 18:00
    _mk(store, "evt-C", 1, "original", 6, BASE + timedelta(minutes=30), BASE + timedelta(minutes=30), BASE + 6 * H, BASE + 9 * H, {"headline": "late arrival", "value": "5"})
    # evt-D: ARCHIVE BACKFILL — published years earlier, genuinely ingested 13:00 (publication never copied to receipt)
    _mk(store, "evt-D", 1, "original", 7, datetime(2020, 3, 1, tzinfo=timezone.utc), datetime(2020, 3, 1, tzinfo=timezone.utc), BASE + H, BASE + 9 * H, {"headline": "old archive doc", "value": "1"})
    return store
