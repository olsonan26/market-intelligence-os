"""Phase 5: NEWS-001..NEWS-009 on adversarial bitemporal fixtures."""
from __future__ import annotations

import unittest
from datetime import timedelta

from mios.contracts.licensing import LicensePolicy, LicenseUse, LicenseViolation, enforce_license
from mios.newsmacro.entities import EntityMapper, EntityMapping
from mios.newsmacro.filings_positioning import Filing, PositioningObservation, filing_visible, positioning_visible
from mios.newsmacro.macro_vintages import MacroSeries, MacroVintage
from mios.newsmacro.provenance_dedup import independent_roots
from mios.timemachine.fixtures import build_adversarial_store, BASE
from mios.timemachine.snapshot import build_snapshot
from mios.timemachine.visibility import VisibilityPolicy

H = timedelta(hours=1)


class NEWS001_CorrectionInvisibleEarly(unittest.TestCase):
    def test_correction_hidden_before_clock(self):
        store = build_adversarial_store()
        snap = build_snapshot(store, (BASE + 3 * H).isoformat(), VisibilityPolicy.PUBLIC_KNOWABLE)
        versions = [e["version"] for e in snap["events"] if e["event_id"] == "evt-A"]
        self.assertNotIn(3, versions)  # correction published at +4h


class NEWS002_RetractionPreservesHistory(unittest.TestCase):
    def test_pre_retraction_view_still_reconstructable(self):
        store = build_adversarial_store()
        early = build_snapshot(store, (BASE + 2 * H).isoformat(), VisibilityPolicy.PUBLIC_KNOWABLE)
        b = [e for e in early["events"] if e["event_id"] == "evt-B"]
        self.assertEqual(len(b), 1)
        self.assertFalse(b[0]["marked_retracted"])  # historical view unchanged by later retraction


class NEWS003_OneIndependentRoot(unittest.TestCase):
    def test_five_reports_one_root(self):
        press_release_sha = "c" * 64
        obs = [{"observation_id": f"obs-{i}", "source_id": f"FIXTURE-OUTLET-{i}",
                "evidence_roots": [press_release_sha]} for i in range(5)]
        r = independent_roots(obs)
        self.assertEqual(r["observation_count"], 5)      # all observations preserved
        self.assertEqual(r["independent_root_count"], 1)  # independence counted once


class NEWS004_FilingClocks(unittest.TestCase):
    def test_dissemination_governs(self):
        f = Filing("f-1", period_end="2025-12-31", accepted_at="2026-02-10T21:05:00+00:00",
                   disseminated_at="2026-02-10T21:35:00+00:00")
        self.assertFalse(filing_visible(f, "2026-02-10T21:20:00+00:00"))
        self.assertTrue(filing_visible(f, "2026-02-10T21:40:00+00:00"))


class NEWS005_MacroVintages(unittest.TestCase):
    def test_vintage_resolution(self):
        s = MacroSeries("FIXTURE-GDP")
        s.add_vintage(MacroVintage("FIXTURE-GDP", "2025-Q4", "2.1", "2026-01-30T13:30:00+00:00", "2026-01-30T13:31:00+00:00"))
        s.add_vintage(MacroVintage("FIXTURE-GDP", "2025-Q4", "2.4", "2026-02-27T13:30:00+00:00", "2026-02-27T13:31:00+00:00"))
        s.add_vintage(MacroVintage("FIXTURE-GDP", "2025-Q4", "2.3", "2026-03-27T13:30:00+00:00", "2026-03-27T13:31:00+00:00"))
        self.assertIsNone(s.value_as_of("2025-Q4", "2026-01-15T00:00:00+00:00"))
        self.assertEqual(s.value_as_of("2025-Q4", "2026-02-01T00:00:00+00:00").value, "2.1")
        self.assertEqual(s.value_as_of("2025-Q4", "2026-03-01T00:00:00+00:00").value, "2.4")
        self.assertEqual(s.value_as_of("2025-Q4", "2026-04-01T00:00:00+00:00").value, "2.3")


class NEWS006_COTLag(unittest.TestCase):
    def test_tuesday_invisible_before_friday(self):
        p = PositioningObservation("cot-1", observed_on="2026-01-06", published_at="2026-01-09T20:30:00+00:00")
        self.assertFalse(positioning_visible(p, "2026-01-07T00:00:00+00:00"))
        self.assertTrue(positioning_visible(p, "2026-01-09T21:00:00+00:00"))


class NEWS007_NoFabricatedReceipt(unittest.TestCase):
    def test_archive_publication_not_receipt(self):
        store = build_adversarial_store()
        rec = build_snapshot(store, "2020-06-01T00:00:00+00:00", VisibilityPolicy.SYSTEM_RECEIVED)
        self.assertEqual([e for e in rec["events"] if e["event_id"] == "evt-D"], [])


class NEWS008_EntityMappingVersioned(unittest.TestCase):
    def test_versioned_and_auditable(self):
        m = EntityMapper()
        m.add(EntityMapping("Fixture Corp", "FIX-XYZ", 0.9, 1, "2026-01-01T00:00:00+00:00", "analyst-a"))
        m.add(EntityMapping("Fixture Corp", "FIX-ABC", 0.97, 2, "2026-02-01T00:00:00+00:00", "analyst-b"))
        early = m.resolve("Fixture Corp", "2026-01-15T00:00:00+00:00")
        late = m.resolve("Fixture Corp", "2026-02-15T00:00:00+00:00")
        self.assertEqual(early.instrument_id, "FIX-XYZ")
        self.assertEqual(late.instrument_id, "FIX-ABC")
        self.assertEqual(len(m.history("Fixture Corp")), 2)
        with self.assertRaises(ValueError):
            m.add(EntityMapping("Fixture Corp", "FIX-Q", 0.5, 9, "2026-03-01T00:00:00+00:00", "x"))


class NEWS009_LicenseBlocksBodyUse(unittest.TestCase):
    def test_prohibited_display_blocked(self):
        no_display = LicensePolicy(license_id="FIXTURE-NEWSWIRE", internal_research=True,
                                   public_display=False, redistribution=False)
        with self.assertRaises(LicenseViolation):
            enforce_license(no_display, LicenseUse.PUBLIC_DISPLAY)
        with self.assertRaises(LicenseViolation):
            enforce_license(no_display, LicenseUse.REDISTRIBUTION)


if __name__ == "__main__":
    unittest.main()
