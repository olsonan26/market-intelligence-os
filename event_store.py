"""SQLite event store behind a neutral port (ADR-0001). Append-only, bitemporal."""
from __future__ import annotations

import base64
import json
import sqlite3
import os
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Sequence, Tuple

from ..contracts.events import CanonicalEvent
from ..adapters.port import RawCapture


class AppendOnlyViolation(RuntimeError):
    """An update or delete was attempted on evidence tables."""


class DuplicateRawPayload(RuntimeError):
    """The same original bytes were captured before (recorded as incident, not an error path)."""


class EventStore:
    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        self._conn.executescript(open(schema_path, encoding="utf-8").read())
        self._conn.commit()

    # ----- raw payloads (Law 5: raw before normalized) -----
    def store_raw(self, cap: RawCapture, raw_sha256: str, system_time_utc: str) -> bool:
        """Returns True if stored, False if identical bytes already present (duplicate)."""
        try:
            self._conn.execute(
                "INSERT INTO raw_payloads (raw_sha256, source_id, provider, content_type, raw_bytes_b64,"
                " received_at_utc, received_prec, received_raw, source_tz, source_sequence, is_test_fixture,"
                " system_time_utc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    raw_sha256, cap.source_id, cap.provider, cap.content_type,
                    base64.b64encode(cap.raw_bytes).decode("ascii"),
                    cap.received_at.utc.isoformat(), cap.received_at.precision.value,
                    cap.received_at.raw_text, cap.received_at.source_timezone,
                    cap.source_sequence, 1 if cap.is_test_fixture else 0, system_time_utc,
                ),
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def load_raw_bytes(self, raw_sha256: str) -> Optional[bytes]:
        row = self._conn.execute(
            "SELECT raw_bytes_b64 FROM raw_payloads WHERE raw_sha256 = ?", (raw_sha256,)
        ).fetchone()
        return base64.b64decode(row["raw_bytes_b64"]) if row else None

    # ----- canonical events (append-only versions) -----
    def append_event(self, event: CanonicalEvent, version: int, version_kind: str) -> None:
        c = event.clocks
        self._conn.execute(
            "INSERT INTO canonical_events (event_id, version, version_kind, schema_name, schema_version,"
            " source_id, provider, source_event_id, source_sequence, instrument_id, event_time_utc,"
            " published_at_utc, ingested_at_utc, system_time_utc, payload_json, raw_sha256, license_json,"
            " evidence_roots, content_hash, is_test_fixture)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                event.event_id, version, version_kind, event.schema_name, event.schema_version,
                event.source.source_id, event.source.provider, event.source.source_event_id,
                event.source.source_sequence,
                event.instrument.instrument_id if event.instrument else None,
                c.event_time.utc.isoformat(),
                c.published_at.utc.isoformat() if c.published_at else None,
                c.ingested_at.utc.isoformat(), c.system_time.utc.isoformat(),
                json.dumps(dict(event.payload), sort_keys=True, separators=(",", ":")),
                event.raw_payload_sha256,
                json.dumps(event.license_policy.to_canonical_dict(), sort_keys=True, separators=(",", ":")),
                json.dumps(list(event.evidence_roots), sort_keys=True, separators=(",", ":")),
                event.content_hash(), 1 if event.is_test_fixture else 0,
            ),
        )
        self._conn.commit()

    def record_incident(self, kind: str, source_id: str, detail: dict, raw_sha256: Optional[str],
                        system_time_utc: str) -> None:
        self._conn.execute(
            "INSERT INTO incidents (kind, source_id, detail_json, raw_sha256, system_time_utc)"
            " VALUES (?,?,?,?,?)",
            (kind, source_id, json.dumps(detail, sort_keys=True, separators=(",", ":")), raw_sha256, system_time_utc),
        )
        self._conn.commit()

    # ----- queries -----
    def all_events(self) -> List[sqlite3.Row]:
        return list(self._conn.execute("SELECT * FROM canonical_events ORDER BY row_id"))

    def incidents(self) -> List[sqlite3.Row]:
        return list(self._conn.execute("SELECT * FROM incidents ORDER BY incident_id"))

    def events_visible_at(self, cutoff_utc: str, governing_clock_sql: str) -> List[sqlite3.Row]:
        """Rows whose governing visibility time <= cutoff. governing_clock_sql is a vetted column expr."""
        assert governing_clock_sql in {
            "ingested_at_utc", "published_at_utc", "event_time_utc",
            "COALESCE(published_at_utc, ingested_at_utc)",
        }
        return list(self._conn.execute(
            f"SELECT * FROM canonical_events WHERE {governing_clock_sql} <= ? ORDER BY row_id", (cutoff_utc,)
        ))

    def try_update_event(self) -> None:
        """Used by tests to prove append-only triggers fire."""
        try:
            self._conn.execute("UPDATE canonical_events SET payload_json = '{}' WHERE row_id = 1")
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            raise AppendOnlyViolation(str(exc)) from exc
        except sqlite3.OperationalError as exc:
            raise AppendOnlyViolation(str(exc)) from exc

    def try_delete_raw(self) -> None:
        try:
            self._conn.execute("DELETE FROM raw_payloads")
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            raise AppendOnlyViolation(str(exc)) from exc
        except sqlite3.OperationalError as exc:
            raise AppendOnlyViolation(str(exc)) from exc
