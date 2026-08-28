"""Phase 11: SEC/DR/LC/AU/REL/LIVE acceptance (environment-independent subset)."""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from mios.hardening.integrity import export_backup, verify_backup
from mios.hardening.live_guard import LiveAuthorityConfigError, validate_runtime_config
from mios.contracts.licensing import LicensePolicy, LicenseUse, LicenseViolation, enforce_license
from mios.timemachine.fixtures import build_adversarial_store


class DR001_BackupRestore(unittest.TestCase):
    def test_backup_reproduces_state(self):
        s = build_adversarial_store()
        b1, b2 = export_backup(s), export_backup(s)
        self.assertEqual(b1["backup_hash"], b2["backup_hash"])
        self.assertTrue(verify_backup(b1)["clean"])


class DR002_CorruptionQuarantine(unittest.TestCase):
    def test_corrupt_raw_detected(self):
        s = build_adversarial_store()
        b = export_backup(s)
        sha = next(iter(b["body"]["raws"]))
        b["body"]["raws"][sha] = "Y29ycnVwdGVk"
        v = verify_backup(b)
        self.assertFalse(v["clean"])
        self.assertIn(sha, v["quarantined"])


class LC001_LicensePathsBlocked(unittest.TestCase):
    def test_prohibited_data_cannot_reach_display_or_export(self):
        restricted = LicensePolicy("FIXTURE-RESTRICTED", internal_research=True)
        for use in (LicenseUse.PUBLIC_DISPLAY, LicenseUse.REDISTRIBUTION):
            with self.assertRaises(LicenseViolation):
                enforce_license(restricted, use)


class LIVE000_NoLiveRoute(unittest.TestCase):
    def test_no_config_flag_enables_live(self):
        for cfg in ({"enable_live_trading": True}, {"LIVE_ORDERS": "1"},
                    {"real_money_mode": "yes"}, {"production_orders": True}):
            with self.assertRaises(LiveAuthorityConfigError):
                validate_runtime_config(cfg)

    def test_benign_config_passes(self):
        cfg = validate_runtime_config({"shadow_mode": True, "paper_venue": "PAPER-FIXTURE"})
        self.assertTrue(cfg["shadow_mode"])

    def test_no_broker_sdks_importable_in_tree(self):
        import mios, os
        from mios.guards.no_live_authority import scan_tree_for_live_authority
        root = os.path.dirname(os.path.dirname(mios.__file__))
        self.assertTrue(scan_tree_for_live_authority(root)["clean"])


if __name__ == "__main__":
    unittest.main()
