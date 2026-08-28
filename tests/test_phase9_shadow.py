"""Phase 9: SH-001..SH-005."""
from __future__ import annotations

import unittest

from mios.shadow.shadow_runner import OrderAuthorityViolation, ShadowRunner


def events(n=8):
    return [{"event_id": f"e-{i}", "is_data": True, "evidence_roots": ["d" * 64],
             "payload": {"price": 100 + i}} for i in range(n)]


def strategy(ev):
    return "would_enter" if ev["payload"]["price"] % 3 == 0 else "no_trade"


class SH001_ZeroOrderAuthority(unittest.TestCase):
    def test_no_broker_attachable(self):
        r = ShadowRunner()
        with self.assertRaises(OrderAuthorityViolation):
            r.broker = object()
        with self.assertRaises(AttributeError):
            r.some_random_attr = 1  # __slots__ prevents any extra state

    def test_no_submit_method_exists(self):
        r = ShadowRunner()
        self.assertFalse(hasattr(r, "submit_paper_order"))
        self.assertFalse(hasattr(r, "submit_order"))


class SH002_LineageReconstruction(unittest.TestCase):
    def test_every_decision_has_lineage(self):
        r = ShadowRunner()
        for d in r.run(events(), strategy):
            self.assertTrue(d.input_event_ids)
            self.assertTrue(d.evidence_roots)
            self.assertEqual(len(d.lineage_hash), 64)


class SH003_StaleHalts(unittest.TestCase):
    def test_stale_gap_produces_no_trade(self):
        evs = events(8)
        for i in range(2, 7):
            evs[i]["is_data"] = False   # 5 consecutive non-data heartbeats
        r = ShadowRunner(max_staleness_indices=3)
        ds = r.run(evs, strategy)
        stale = [d for d in ds if "stale data" in d.reasons[0]]
        self.assertTrue(stale)
        for d in stale:
            self.assertEqual(d.would_action, "no_trade")


class SH004_RestartNoDuplicates(unittest.TestCase):
    def test_catchup_skips_seen_events(self):
        evs = events(8)
        r = ShadowRunner()
        r.run(evs[:5], strategy)
        # 'restart replay catch-up': re-feed the full stream; seen events are skipped
        ds = r.run(evs, strategy)
        self.assertEqual(len(ds), 8)
        self.assertEqual(len({d.input_event_ids[0] for d in ds}), 8)


class SH005_ProviderReconnectRecovery(unittest.TestCase):
    def test_duplicate_events_after_reconnect(self):
        evs = events(4) + events(4)  # provider resends everything after reconnect
        r = ShadowRunner()
        ds = r.run(evs, strategy)
        self.assertEqual(len(ds), 4)  # no duplicate decisions


if __name__ == "__main__":
    unittest.main()
