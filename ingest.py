"""Ingestion: RawCapture -> raw store -> canonical event, with incident evidence (Laws 5, 12)."""
from __future__ import annotations

import json
from typing import Iterable, List, Optional

from ..adapters.port import RawCapture
from ..contracts.clocks import FourClocks
from ..contracts.events import CanonicalEvent, SourceRef
from ..contracts.hashing import sha256_hex
from ..contracts.instruments import InstrumentRef
from ..contracts.licensing import LicensePolicy
from ..contracts.timestamps import PointInTimeTimestamp, TimePrecision
from ..storage.event_store import EventStore

FIXTURE_LICENSE = LicensePolicy(license_id="FIXTURE-LICENSE-INTERNAL-ONLY", internal_research=True,
                                derived_signals=True, redistribution=False, public_display=False)


class IngestResult:
    def __init__(self) -> None:
        self.stored: List[str] = []
        self.duplicates: List[str] = []
        self.gaps: List[dict] = []
        self.rejected: List[dict] = []


def ingest(captures: Iterable[RawCapture], store: EventStore, system_clock, instrument: InstrumentRef,
           license_policy: Optional[LicensePolicy] = None) -> IngestResult:
    result = IngestResult()
    last_seq: Optional[int] = None
    policy = license_policy or FIXTURE_LICENSE
    for cap in captures:
        sys_now = system_clock.now().isoformat()
        raw_hash = sha256_hex(cap.raw_bytes)

        # sequence gap detection BEFORE storage decisions (Law 12)
        if cap.source_sequence is not None and last_seq is not None and cap.source_sequence > last_seq + 1:
            gap = {"expected": last_seq + 1, "got": cap.source_sequence}
            store.record_incident("gap", cap.source_id, gap, raw_hash, sys_now)
            result.gaps.append(gap)
        if cap.source_sequence is not None:
            last_seq = max(last_seq, cap.source_sequence) if last_seq is not None else cap.source_sequence

        stored = store.store_raw(cap, raw_hash, sys_now)
        if not stored:
            store.record_incident("duplicate", cap.source_id, {"raw_sha256": raw_hash}, raw_hash, sys_now)
            result.duplicates.append(raw_hash)
            continue

        # normalize AFTER raw bytes are safely stored (Law 5)
        try:
            payload = json.loads(cap.raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            detail = {"error": type(exc).__name__, "message": str(exc)[:200]}
            store.record_incident("rejected_payload", cap.source_id, detail, raw_hash, sys_now)
            result.rejected.append(detail)
            continue

        event = CanonicalEvent(
            event_id=f"{cap.source_id}:{cap.source_sequence}:{raw_hash[:12]}",
            schema_name="mios.canonical_event",
            schema_version="1.0.0",
            source=SourceRef(source_id=cap.source_id, provider=cap.provider,
                             source_event_id=str(cap.source_sequence), source_sequence=cap.source_sequence),
            clocks=FourClocks(
                event_time=PointInTimeTimestamp(
                    utc=cap.received_at.utc, precision=cap.received_at.precision,
                    raw_text=str(payload.get("ts")), source_timezone=cap.received_at.source_timezone),
                published_at=cap.received_at,
                ingested_at=cap.received_at,
                system_time=PointInTimeTimestamp(
                    utc=system_clock.now(), precision=TimePrecision.MICROSECOND),
            ),
            payload=payload,
            raw_payload_sha256=raw_hash,
            license_policy=policy,
            evidence_roots=(raw_hash,),
            instrument=instrument,
            is_test_fixture=cap.is_test_fixture,
        )
        store.append_event(event, version=1, version_kind="original")
        result.stored.append(event.event_id)
    return result
