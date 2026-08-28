"""Phase 2 Time Machine acceptance tests TM-001..TM-007 (spec section 13)."""
from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from mios.timemachine.fixtures import build_adversarial_store, BASE, _mk
from mios.timemachine.snapshot import build_snapshot, explain_event
from mios.timemachine.visibility import VisibilityPolicy, decide_visibility
from datetime import timedelta

H = timedelta(hours=1)


def iso(dt):
    return dt.isoformat()


class TM001_CutoffExcludesFuture(unittest.TestCase):
    """No version is visible before its own governing time (no future leakage)."""

    def test_cutoff_before_everything(self):
        store = build_adversarial_store()
        snap = build_snapshot(store, iso(BASE), VisibilityPolicy.SYSTEM_RECEIVED)
        self.assertEqual(len(snap["events"]), 0)
        for d in snap["decisions"]:
            self.assertFalse(d["visible"])
            self.assertIn("knowledge did not exist yet", d["reason"])

    def test_midday_cutoff_sees_only_v1(self):
        store = build_adversarial_store()
        snap = build_snapshot(store, iso(BASE + timedelta(minutes=30)), VisibilityPolicy.SYSTEM_RECEIVED)
        ids = [(e["event_id"], e["version"]) for e in snap["events"]]
        self.assertEqual(ids, [("evt-A", 1)])


class TM002_RevisionsAndCorrections(unittest.TestCase):
    """Later versions appear only after their own visibility time; earlier remain."""

    def test_progression(self):
        store = build_adversarial_store()
        cut1 = build_snapshot(store, iso(BASE + 1 * H), VisibilityPolicy.PUBLIC_KNOWABLE)
        vers = [(e["event_id"], e["version"]) for e in cut1["events"] if e["event_id"] == "evt-A"]
        self.assertEqual(vers, [("evt-A", 1)])
        cut2 = build_snapshot(store, iso(BASE + 2 * H), VisibilityPolicy.PUBLIC_KNOWABLE)
        vers = [(e["event_id"], e["version"]) for e in cut2["events"] if e["event_id"] == "evt-A"]
        self.assertEqual(vers, [("evt-A", 1), ("evt-A", 2)])
        cut3 = build_snapshot(store, iso(BASE + 4 * H), VisibilityPolicy.PUBLIC_KNOWABLE)
        vers = [(e["event_id"], e["version"]) for e in cut3["events"] if e["event_id"] == "evt-A"]
        self.assertEqual(vers, [("evt-A", 1), ("evt-A", 2), ("evt-A", 3)])


class TM003_Retraction(unittest.TestCase):
    """A visible retraction marks prior versions retracted; nothing is deleted."""

    def test_before_retraction(self):
        store = build_adversarial_store()
        snap = build_snapshot(store, iso(BASE + 2 * H), VisibilityPolicy.PUBLIC_KNOWABLE)
        b = [e for e in snap["events"] if e["event_id"] == "evt-B"]
        self.assertEqual(len(b), 1)
        self.assertFalse(b[0]["marked_retracted"])

    def test_after_retraction(self):
        store = build_adversarial_store()
        snap = build_snapshot(store, iso(BASE + 3 * H + timedelta(minutes=5)), VisibilityPolicy.PUBLIC_KNOWABLE)
        b = {e["version"]: e for e in snap["events"] if e["event_id"] == "evt-B"}
        self.assertIn(1, b); self.assertIn(2, b)
        self.assertTrue(b[1]["marked_retracted"])   # prior version visible but marked
        self.assertEqual(b[2]["version_kind"], "retraction")


class TM004_LateArrival(unittest.TestCase):
    """published long before ingestion: public-knowable vs system-received disagree correctly."""

    def test_policies_disagree(self):
        store = build_adversarial_store()
        cutoff = iso(BASE + 2 * H)  # 14:00
        pub = build_snapshot(store, cutoff, VisibilityPolicy.PUBLIC_KNOWABLE)
        rec = build_snapshot(store, cutoff, VisibilityPolicy.SYSTEM_RECEIVED)
        pub_ids = {(e["event_id"], e["version"]) for e in pub["events"]}
        rec_ids = {(e["event_id"], e["version"]) for e in rec["events"]}
        self.assertIn(("evt-C", 1), pub_ids)      # publicly knowable at 12:30
        self.assertNotIn(("evt-C", 1), rec_ids)   # system had NOT received it until 18:00
        expl = explain_event(store, cutoff, VisibilityPolicy.SYSTEM_RECEIVED, "evt-C")
        self.assertFalse(expl[0]["visible"])
        self.assertIn("ingested_at", expl[0]["governing_clock"])


class TM005_ArchiveBackfill(unittest.TestCase):
    """Archive publication time is never copied into receipt time."""

    def test_backfill(self):
        store = build_adversarial_store()
        early = build_snapshot(store, iso(datetime(2020, 6, 1, tzinfo=timezone.utc)), VisibilityPolicy.SYSTEM_RECEIVED)
        self.assertEqual(len([e for e in early["events"] if e["event_id"] == "evt-D"]), 0)
        after = build_snapshot(store, iso(BASE + H), VisibilityPolicy.SYSTEM_RECEIVED)
        self.assertEqual(len([e for e in after["events"] if e["event_id"] == "evt-D"]), 1)
        pub2020 = build_snapshot(store, iso(datetime(2020, 6, 1, tzinfo=timezone.utc)), VisibilityPolicy.PUBLIC_KNOWABLE)
        self.assertEqual(len([e for e in pub2020["events"] if e["event_id"] == "evt-D"]), 1)


class TM006_SnapshotStability(unittest.TestCase):
    """A sealed snapshot's hash is stable after later ingestion."""

    def test_stable_after_new_data(self):
        store = build_adversarial_store()
        cutoff = iso(BASE + 2 * H)
        before = build_snapshot(store, cutoff, VisibilityPolicy.SYSTEM_RECEIVED)
        _mk(store, "evt-E", 1, "original", 99, BASE + 8 * H, BASE + 8 * H, BASE + 8 * H, BASE + 10 * H,
            {"headline": "much later", "value": "9"})
        after = build_snapshot(store, cutoff, VisibilityPolicy.SYSTEM_RECEIVED)
        self.assertEqual(before["snapshot_hash"], after["snapshot_hash"])


class TM007_ExplanationsAndReproducibility(unittest.TestCase):
    """Every decision names its governing clock/policy; identical snapshots => identical hashes."""

    def test_every_decision_explained(self):
        store = build_adversarial_store()
        for policy in VisibilityPolicy:
            for d in decide_visibility(store, iso(BASE + 2 * H), policy):
                self.assertTrue(d.reason)
                self.assertIn(d.policy, (policy.value,))
                self.assertTrue(d.governing_clock)

    def test_identical_snapshots_identical_hashes(self):
        h1 = build_snapshot(build_adversarial_store(), iso(BASE + 3 * H), VisibilityPolicy.PUBLIC_KNOWABLE)["snapshot_hash"]
        h2 = build_snapshot(build_adversarial_store(), iso(BASE + 3 * H), VisibilityPolicy.PUBLIC_KNOWABLE)["snapshot_hash"]
        self.assertEqual(h1, h2)

    def test_trace_to_immutable_bytes(self):
        store = build_adversarial_store()
        snap = build_snapshot(store, iso(BASE + 4 * H), VisibilityPolicy.PUBLIC_KNOWABLE)
        for e in snap["events"]:
            raw = store.load_raw_bytes(e["raw_sha256"])
            self.assertIsNotNone(raw)
            self.assertEqual(json.loads(raw.decode()), e["payload"])


if __name__ == "__main__":
    unittest.main()
