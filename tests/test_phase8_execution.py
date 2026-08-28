"""Phase 8: EX-001..EX-004 + no-live guard on broker ports."""
from __future__ import annotations

import unittest
from decimal import Decimal

from mios.execution.broker_ports import SandboxBrokerPort
from mios.execution.paper_broker import (
    CapabilityError, PaperBroker, PaperLedger, TradeIntent, VenueCapabilities, reconcile,
)
from mios.simulation.engine_port import EntitlementPending

CAPS = VenueCapabilities(venue_id="PAPER-FIXTURE", supports_oco=False)


class EX001_RestartReconstruction(unittest.TestCase):
    def test_partial_fill_restart(self):
        ledger = PaperLedger()
        broker = PaperBroker(CAPS, ledger)
        oid = broker.submit_paper_order(TradeIntent("i-1", "FIX-XYZ", "buy", Decimal("10")), "k-1")
        broker.fill(oid, Decimal("4"), Decimal("100.10"))
        state_before = ledger.reconstruct()
        # 'restart': rebuild broker state purely from the persisted ledger entries
        ledger2 = PaperLedger()
        ledger2.entries = [dict(e) for e in ledger.entries]
        state_after = ledger2.reconstruct()
        self.assertEqual(state_before["state_hash"], state_after["state_hash"])
        self.assertEqual(state_after["orders"][oid]["remaining"], "6")
        self.assertEqual(state_after["orders"][oid]["status"], "partially_filled")
        self.assertEqual(state_after["position"], "4")


class EX002_NoSilentOCOEmulation(unittest.TestCase):
    def test_unsupported_oco_rejected(self):
        broker = PaperBroker(CAPS, PaperLedger())
        with self.assertRaises(CapabilityError):
            broker.submit_paper_order(TradeIntent("i-2", "FIX-XYZ", "buy", Decimal("1"),
                                                  requires_oco=True), "k-2")


class EX003_Idempotency(unittest.TestCase):
    def test_same_key_no_duplicate(self):
        ledger = PaperLedger()
        broker = PaperBroker(CAPS, ledger)
        intent = TradeIntent("i-3", "FIX-XYZ", "buy", Decimal("5"))
        oid1 = broker.submit_paper_order(intent, "k-3")
        oid2 = broker.submit_paper_order(intent, "k-3")
        self.assertEqual(oid1, oid2)
        accepted = [e for e in ledger.entries if e["kind"] == "order_accepted"]
        self.assertEqual(len(accepted), 1)


class EX004_SnapshotReconciliation(unittest.TestCase):
    def test_disconnect_snapshot_reconciles(self):
        ledger = PaperLedger()
        broker = PaperBroker(CAPS, ledger)
        oid = broker.submit_paper_order(TradeIntent("i-4", "FIX-XYZ", "buy", Decimal("10")), "k-4")
        broker.fill(oid, Decimal("10"), Decimal("100"))
        state = ledger.reconstruct()
        venue_snapshot = {"position": "10", "orders": {oid: {"remaining": "0", "status": "filled"}}}
        r = reconcile(state, venue_snapshot)
        self.assertTrue(r["reconciled"], r["mismatches"])

    def test_mismatch_detected(self):
        ledger = PaperLedger()
        broker = PaperBroker(CAPS, ledger)
        oid = broker.submit_paper_order(TradeIntent("i-5", "FIX-XYZ", "buy", Decimal("10")), "k-5")
        broker.fill(oid, Decimal("10"), Decimal("100"))
        r = reconcile(ledger.reconstruct(), {"position": "7", "orders": {}})
        self.assertFalse(r["reconciled"])
        self.assertTrue(any(m["field"] == "position" for m in r["mismatches"]))


class NoLiveBrokerAccess(unittest.TestCase):
    def test_external_venues_entitlement_pending(self):
        for venue in ("IBKR", "OANDA_V20", "KRAKEN"):
            with self.assertRaises(EntitlementPending):
                SandboxBrokerPort(venue)


if __name__ == "__main__":
    unittest.main()
