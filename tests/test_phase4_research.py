"""Phase 4: VAL-001..VAL-009."""
from __future__ import annotations

import unittest
from decimal import Decimal

from mios.research.features import FutureLeakError, PointInTimeFeatureBuilder
from mios.research.validation import (
    ChampionChallengerRegistry, EvaluationOutcome, ExperimentRegistry, PreRegistration,
    evaluate_candidate, purged_chronological_splits,
)
from mios.timemachine.fixtures import build_adversarial_store, BASE
from mios.timemachine.visibility import VisibilityPolicy
from datetime import timedelta

H = timedelta(hours=1)
PRICES = [Decimal(s) for s in ("100", "101", "102", "101", "103", "104", "103", "105", "106", "107")]


def registry():
    r = ExperimentRegistry()
    return r


class VAL001_FutureLeakRejected(unittest.TestCase):
    def test_leaky_feature_raises(self):
        store = build_adversarial_store()
        fb = PointInTimeFeatureBuilder(store, (BASE + 2 * H).isoformat())
        with self.assertRaises(FutureLeakError):
            fb.declare_input((BASE + 5 * H).isoformat())

    def test_leaky_experiment_rejected(self):
        r = registry()
        r.preregister(PreRegistration("exp-leak", "leaky", {"net": 0.0}, "2026-01-05T00:00:00+00:00"))
        out = evaluate_candidate("exp-leak", PRICES, [1] * 10, Decimal("0.5"), r, used_future_leak=True)
        self.assertEqual(out.status, "REJECTED_LEAK")
        self.assertFalse(out.accepted)


class VAL002_PurgedSplits(unittest.TestCase):
    def test_purge_gap_removes_overlap(self):
        folds = purged_chronological_splits(n=100, n_folds=5, label_horizon=3)
        for train, test in folds:
            self.assertLess(max(train), min(test) - 2)  # >= label_horizon gap


class VAL003_CostsFlipWinner(unittest.TestCase):
    def test_zero_cost_winner_rejected_after_costs(self):
        r = registry()
        r.preregister(PreRegistration("exp-cost", "overtrader", {"net": 0.0}, "2026-01-05T00:00:00+00:00"))
        churny = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1]
        zero_cost = evaluate_candidate("exp-cost", PRICES, churny, Decimal("0"), r)
        r.preregister(PreRegistration("exp-cost2", "overtrader-costed", {"net": 0.0}, "2026-01-05T00:00:01+00:00"))
        costed = evaluate_candidate("exp-cost2", PRICES, churny, Decimal("2"), r)
        self.assertGreater(zero_cost.net_return, costed.net_return)
        self.assertFalse(costed.accepted)


class VAL004_RepeatedTestingBounded(unittest.TestCase):
    def test_attempts_recorded_and_alpha_adjusted(self):
        r = registry()
        for i in range(4):
            r.preregister(PreRegistration(f"exp-h{i}", "same hypothesis", {"net": 0.0}, f"2026-01-05T00:00:0{i}+00:00"))
        entry = r.record_result("exp-h3", {"net": "1"})
        self.assertEqual(entry["hypothesis_attempts"], 4)
        self.assertAlmostEqual(entry["adjusted_alpha"], 0.0125)


class VAL005_Reproducibility(unittest.TestCase):
    def test_feature_set_hash_reproducible(self):
        h1 = PointInTimeFeatureBuilder(build_adversarial_store(), (BASE + 4 * H).isoformat()).feature_set()["feature_set_hash"]
        h2 = PointInTimeFeatureBuilder(build_adversarial_store(), (BASE + 4 * H).isoformat()).feature_set()["feature_set_hash"]
        self.assertEqual(h1, h2)


class VAL006_FragileModelFails(unittest.TestCase):
    def test_perturbation_rejects(self):
        r = registry()
        r.preregister(PreRegistration("exp-frag", "fragile", {"net": 0.0}, "2026-01-05T00:00:00+00:00"))
        lucky = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0]     # buys before up-moves (lucky fit)
        shifted = [0, 0, 1, 0, 0, 1, 0, 0, 0, 0]   # same rule shifted: buys before down-moves
        out = evaluate_candidate("exp-frag", PRICES, lucky, Decimal("0.1"), r,
                                 robustness_shift_signals=shifted)
        self.assertIn("VAL-006", " ".join(out.reasons))


class VAL007_ThresholdsLocked(unittest.TestCase):
    def test_higher_headline_return_still_not_eligible(self):
        cc = ChampionChallengerRegistry({"net": 1.0, "robustness": 0.5})
        state = cc.consider("challenger-A", {"net": 5.0, "robustness": 0.1})
        self.assertEqual(state, "NOT_ELIGIBLE")
        self.assertIsNone(cc.champion)


class VAL008_FeatureProvenance(unittest.TestCase):
    def test_every_feature_traces_inputs(self):
        fs = PointInTimeFeatureBuilder(build_adversarial_store(), (BASE + 4 * H).isoformat()).feature_set()
        for f in fs["features"]:
            self.assertTrue(f["inputs"], "feature must trace to point-in-time inputs")
            for _, version in f["inputs"]:
                self.assertGreaterEqual(version, 1)


class VAL009_NoTradeWins(unittest.TestCase):
    def test_insufficient_edge_loses_to_no_trade(self):
        r = registry()
        r.preregister(PreRegistration("exp-weak", "weak edge", {"net": 0.0}, "2026-01-05T00:00:00+00:00"))
        weak = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        out = evaluate_candidate("exp-weak", PRICES, weak, Decimal("3"), r)
        self.assertFalse(out.accepted)
        self.assertIn("no-trade", out.reasons[0])

    def test_negative_results_retained(self):
        r = registry()
        r.preregister(PreRegistration("exp-neg", "loser", {"net": 0.0}, "2026-01-05T00:00:00+00:00"))
        evaluate_candidate("exp-neg", PRICES, [-1] * 10, Decimal("1"), r)
        self.assertEqual(len(r.all_results()), 1)  # rejected result stored permanently


if __name__ == "__main__":
    unittest.main()
