"""Phase 10: UI-001..UI-004."""
from __future__ import annotations

import unittest

from mios.audit.audit_surface import AuditSurface, DisplayMetric, RoleError


class UI001_DeepLinks(unittest.TestCase):
    def test_metric_requires_lineage(self):
        m = DisplayMetric("m1", "Net EV", "-0.35", "fixture",
                          {"event_versions": [["evt-A", 3]], "snapshot_hash": "x" * 64})
        r = m.render()
        self.assertIn("deep_link", r)
        with self.assertRaises(ValueError):
            DisplayMetric("m2", "Naked number", "42", "fixture", {}).render()


class UI002_DisplayCannotMutate(unittest.TestCase):
    def test_projection_read_only(self):
        s = AuditSurface({"net_ev": "-0.35", "decision": "no_trade"})
        with self.assertRaises(TypeError):
            s.canonical["net_ev"] = "99"
        self.assertEqual(s.canonical["net_ev"], "-0.35")

    def test_hash_stable(self):
        a = AuditSurface({"x": 1}); b = AuditSurface({"x": 1})
        self.assertEqual(a.canonical_hash(), b.canonical_hash())


class UI003_RoleRestrictions(unittest.TestCase):
    def test_viewer_blocked(self):
        s = AuditSurface({})
        with self.assertRaises(RoleError):
            s.act("viewer", "approve_queue")
        with self.assertRaises(RoleError):
            s.act("operator", "kill_switch")
        self.assertEqual(s.act("risk_officer", "kill_switch"), "kill_switch:permitted")


class UI004_SourceStatesUnconfusable(unittest.TestCase):
    def test_badges_mandatory_and_distinct(self):
        seen = set()
        for state in ("fixture", "shadow", "paper", "real"):
            r = DisplayMetric("m", "Metric", "1", state, {"decision_id": "sd-1"}).render()
            self.assertTrue(r["label"].startswith(f"[{r['badge']}]"))
            seen.add(r["badge"])
        self.assertEqual(len(seen), 4)

    def test_unknown_state_rejected(self):
        with self.assertRaises(ValueError):
            DisplayMetric("m", "Metric", "1", "live", {"decision_id": "sd-1"}).render()


if __name__ == "__main__":
    unittest.main()
