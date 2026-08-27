"""Phase 1: fixture vertical slice — capture, duplicates, gaps, rejects, append-only, deterministic replay."""
from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from mios.adapters.fixture_adapter import FixtureMarketDataAdapter, FIXTURE_SOURCE_ID
from mios.adapters.port import RawCapture
from mios.contracts.clocks import DeterministicClock
from mios.contracts.instruments import InstrumentRef
from mios.contracts.timestamps import PointInTimeTimestamp, TimePrecision
from mios.pipeline.ingest import ingest
from mios.pipeline.replay import replay
from mios.storage.event_store import AppendOnlyViolation, EventStore

UTC0 = datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc)
INSTR = InstrumentRef(instrument_id="FIX-XYZ", symbol="FIXTURE-XYZ", venue="FIXTURE", asset_class="equity")


def fresh() -> tuple:
    store = EventStore(":memory:")
    sysclock = DeterministicClock(datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc), step_seconds=0.25)
    return store, sysclock


class TestHappyPath(unittest.TestCase):
    def test_capture_normalize_replay(self):
        store, sysclock = fresh()
        caps = list(FixtureMarketDataAdapter(count=5).capture())
        result = ingest(caps, store, sysclock, INSTR)
        self.assertEqual(len(result.stored), 5)
        self.assertEqual(result.duplicates, [])
        rep = replay(store)
        self.assertEqual(rep["count"], 5)
        # raw bytes retrievable and identical
        for r in store.all_events():
            raw = store.load_raw_bytes(r["raw_sha256"])
            self.assertIsNotNone(raw)
            self.assertEqual(json.loads(raw.decode()), json.loads(r["payload_json"]))

    def test_every_event_labeled_fixture(self):
        store, sysclock = fresh()
        ingest(FixtureMarketDataAdapter(count=3).capture(), store, sysclock, INSTR)
        for r in store.all_events():
            self.assertEqual(r["is_test_fixture"], 1)
            self.assertTrue(r["source_id"].startswith("FIXTURE-"))
            self.assertIn("NOT-REAL-MARKET-DATA", json.loads(r["payload_json"])["banner"])


class TestDuplicates(unittest.TestCase):
    def test_duplicate_bytes_become_incident_not_second_event(self):
        store, sysclock = fresh()
        caps = list(FixtureMarketDataAdapter(count=3).capture())
        ingest(caps, store, sysclock, INSTR)
        result2 = ingest(caps, store, sysclock, INSTR)
        self.assertEqual(len(result2.stored), 0)
        self.assertEqual(len(result2.duplicates), 3)
        kinds = [i["kind"] for i in store.incidents()]
        self.assertEqual(kinds.count("duplicate"), 3)
        self.assertEqual(len(store.all_events()), 3)


class TestGaps(unittest.TestCase):
    def test_sequence_gap_recorded(self):
        store, sysclock = fresh()
        caps = list(FixtureMarketDataAdapter(count=5).capture())
        gapped = [caps[0], caps[1], caps[4]]  # skip seq 2,3
        result = ingest(gapped, store, sysclock, INSTR)
        self.assertEqual(len(result.gaps), 1)
        self.assertEqual(result.gaps[0], {"expected": 2, "got": 4})
        self.assertIn("gap", [i["kind"] for i in store.incidents()])


class TestRejectedPayloads(unittest.TestCase):
    def test_invalid_bytes_stored_raw_and_rejected(self):
        store, sysclock = fresh()
        bad = RawCapture(
            source_id=FIXTURE_SOURCE_ID, provider="fixture", raw_bytes=b"\x00\xffnot-json",
            received_at=PointInTimeTimestamp(utc=UTC0, precision=TimePrecision.SECOND),
            content_type="application/json", source_sequence=0, is_test_fixture=True)
        result = ingest([bad], store, sysclock, INSTR)
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(len(store.all_events()), 0)
        # raw bytes preserved even though normalization failed (raw before normalized)
        import hashlib
        h = hashlib.sha256(bad.raw_bytes).hexdigest()
        self.assertEqual(store.load_raw_bytes(h), bad.raw_bytes)
        self.assertIn("rejected_payload", [i["kind"] for i in store.incidents()])


class TestAppendOnly(unittest.TestCase):
    def test_update_and_delete_rejected(self):
        store, sysclock = fresh()
        ingest(FixtureMarketDataAdapter(count=2).capture(), store, sysclock, INSTR)
        with self.assertRaises(AppendOnlyViolation):
            store.try_update_event()
        with self.assertRaises(AppendOnlyViolation):
            store.try_delete_raw()


class TestDeterministicReplay(unittest.TestCase):
    def test_identical_runs_identical_hashes(self):
        def run() -> str:
            store, sysclock = fresh()
            ingest(FixtureMarketDataAdapter(count=5).capture(), store, sysclock, INSTR)
            return replay(store)["replay_hash"]
        self.assertEqual(run(), run())

    def test_order_independent_of_arrival_shuffle(self):
        store1, c1 = fresh()
        caps = list(FixtureMarketDataAdapter(count=5).capture())
        ingest(caps, store1, c1, INSTR)
        h1 = replay(store1)["replay_hash"]
        store2, c2 = fresh()
        ingest(list(reversed(caps)), store2, c2, INSTR)
        h2 = replay(store2)["replay_hash"]
        self.assertEqual(h1, h2)  # total order sorts identically regardless of arrival


if __name__ == "__main__":
    unittest.main()
