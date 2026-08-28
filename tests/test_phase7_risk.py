"""Phase 7: PR-001..003, EV-001..002, RS-001..004, NT-001."""
from __future__ import annotations

import unittest
from decimal import Decimal

from mios.risk.calibration import Calibrator
from mios.risk.expected_value import FrictionConfig, net_expected_value
from mios.risk.risk_engine import (
    KillSwitchRegistry, RiskDecision, RiskPolicy, RiskState, TradeIntentRequest, decide, gate_trade_intent,
)

POLICY = RiskPolicy("fixture-policy", max_staleness_seconds=60,
                    max_correlated_exposure=Decimal("100"), margin_usage_limit=Decimal("0.8"))
FRICTIONS = FrictionConfig(*(Decimal(x) for x in ("0.5", "0.3", "0.4", "0.1", "0.1", "0.1", "0.2", "0.3")))


def deterministic_calibrator(bias=0.0):
    """Deterministic (seedless) calibration history: forecasts arithmetic, outcomes match frequency."""
    c = Calibrator(n_bins=10, min_samples_per_bin=20)
    for i in range(400):
        f = ((i * 37) % 100) / 100.0
        outcome = 1 if ((i * 53) % 100) / 100.0 < min(1.0, max(0.0, f + bias)) else 0
        c.observe(f, outcome)
    return c


class PR001_BinsMatchReality(unittest.TestCase):
    def test_bins_within_tolerance(self):
        c = deterministic_calibrator()
        for b in c.bins():
            if b.realized_rate is not None:
                center = (b.lower + b.upper) / 2
                self.assertLess(abs(b.realized_rate - center), 0.2)


class PR002_SampleSizeAndUncertainty(unittest.TestCase):
    def test_display_carries_evidence(self):
        c = deterministic_calibrator()
        d = c.displayed_probability(0.7)
        self.assertFalse(d["abstain"])
        self.assertIn("sample_size", d)
        self.assertIn("uncertainty", d)
        self.assertTrue(d["raw_confidence_never_displayed"])

    def test_sparse_bin_abstains(self):
        c = Calibrator(min_samples_per_bin=20)
        for _ in range(5):
            c.observe(0.71, 1)
        d = c.displayed_probability(0.7)
        self.assertTrue(d["abstain"])
        self.assertIsNone(d["display"])


class PR003_DriftPolicy(unittest.TestCase):
    def test_shift_triggers_recalibration(self):
        c = deterministic_calibrator()
        result = c.drift_check([0.95] * 50)
        self.assertTrue(result["shift_detected"])
        self.assertEqual(result["action"], "abstain_and_recalibrate")


class EV001_AllFrictionsIncluded(unittest.TestCase):
    def test_every_friction_configured(self):
        ev = net_expected_value(Decimal("0.6"), Decimal("10"), Decimal("5"), FRICTIONS)
        self.assertEqual(len(ev["frictions"]), 8)
        self.assertEqual(Decimal(ev["friction_total"]), Decimal("2.0"))


class EV002_PositiveRawNegativeNet(unittest.TestCase):
    def test_flip_to_no_trade(self):
        ev = net_expected_value(Decimal("0.55"), Decimal("4"), Decimal("3"), FRICTIONS)
        self.assertGreater(Decimal(ev["raw_ev"]), 0)
        self.assertLess(Decimal(ev["net_ev"]), 0)
        c = deterministic_calibrator()
        d = decide(TradeIntentRequest("i-1", "FIX-XYZ", "buy", Decimal("10"), "g1"),
                   RiskState(10, {}, Decimal("0"), Decimal("1000")), POLICY)
        gate = gate_trade_intent(c.displayed_probability(0.7), ev, d)
        self.assertEqual(gate["action"], "no_trade")
        self.assertIsNone(gate["trade_intent"])


class RS001_Staleness(unittest.TestCase):
    def test_stale_blocks_entries_not_exits(self):
        state = RiskState(999, {}, Decimal("0"), Decimal("1000"))
        entry = decide(TradeIntentRequest("i-2", "FIX-XYZ", "buy", Decimal("10"), "g1"), state, POLICY)
        self.assertEqual(entry.action, "no_trade")
        exit_ = decide(TradeIntentRequest("i-3", "FIX-XYZ", "sell", Decimal("10"), "g1",
                                          is_risk_reducing=True), state, POLICY)
        self.assertEqual(exit_.action, "approve")


class RS002_Concentration(unittest.TestCase):
    def test_correlated_signals_capped(self):
        state = RiskState(10, {"energy": Decimal("95")}, Decimal("0"), Decimal("1000"))
        d = decide(TradeIntentRequest("i-4", "FIX-ABC", "buy", Decimal("10"), "energy"), state, POLICY)
        self.assertEqual(d.action, "no_trade")
        self.assertIn("correlated exposure", d.reasons[0])


class RS003_Margin(unittest.TestCase):
    def test_margin_breach_rejected(self):
        state = RiskState(10, {}, Decimal("790"), Decimal("1000"))
        d = decide(TradeIntentRequest("i-5", "FIX-XYZ", "buy", Decimal("50"), "g1"), state, POLICY)
        self.assertEqual(d.action, "no_trade")


class RS004_KillSwitches(unittest.TestCase):
    def test_deterministic_authenticated_logged(self):
        kills = KillSwitchRegistry(authorized_operators=("alex",))
        with self.assertRaises(PermissionError):
            kills.set("global", True, "intruder")
        kills.set("global", True, "alex")
        state = RiskState(10, {}, Decimal("0"), Decimal("1000"), {"global": True})
        d = decide(TradeIntentRequest("i-6", "FIX-XYZ", "buy", Decimal("1"), "g1"), state, POLICY, kills)
        self.assertEqual(d.action, "no_trade")
        self.assertEqual(kills.log()[0]["operator"], "alex")

    def test_decision_reproducible(self):
        state = RiskState(10, {}, Decimal("0"), Decimal("1000"))
        d1 = decide(TradeIntentRequest("i-7", "FIX-XYZ", "buy", Decimal("1"), "g1"), state, POLICY)
        d2 = decide(TradeIntentRequest("i-7", "FIX-XYZ", "buy", Decimal("1"), "g1"), state, POLICY)
        self.assertEqual(d1.decision_hash, d2.decision_hash)


class NT001_AbstentionGate(unittest.TestCase):
    def test_insufficient_calibration_no_intent(self):
        sparse = Calibrator(min_samples_per_bin=20)
        ev = net_expected_value(Decimal("0.7"), Decimal("10"), Decimal("2"), FRICTIONS)
        state = RiskState(10, {}, Decimal("0"), Decimal("1000"))
        d = decide(TradeIntentRequest("i-8", "FIX-XYZ", "buy", Decimal("1"), "g1"), state, POLICY)
        gate = gate_trade_intent(sparse.displayed_probability(0.7), ev, d)
        self.assertEqual(gate["action"], "no_trade")
        self.assertIn("NT-001", gate["reason"])


if __name__ == "__main__":
    unittest.main()
