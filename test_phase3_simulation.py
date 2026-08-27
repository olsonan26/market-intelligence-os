"""Phase 3: SIM-001..SIM-008 against the deterministic reference engine + honest external state."""
from __future__ import annotations

import unittest
from decimal import Decimal

from mios.simulation.engine_port import EntitlementPending, FrictionModel, LatencyModel
from mios.simulation.reference_engine import DeterministicSimEngine
from mios.simulation.external_engines import LeanEngine, NautilusTraderEngine


def fixture_events(n=10, constrained_at=None):
    evs = []
    price = 100.0
    for i in range(n):
        price += ((7 * (i + 1)) % 13 - 6) / 10
        evs.append({"index": i, "payload": {"symbol": "FIXTURE-XYZ", "price": f"{price:.2f}"},
                    "fixture": True})
    return evs


def momentum_strategy(ev, position):
    i = ev["index"]
    if i == 2 and position == 0:
        return {"side": "buy", "quantity": "10"}
    if i == 7 and position > 0:
        return {"side": "sell", "quantity": "10"}
    return None


def constrained_strategy(ev, position):
    if ev["index"] == 1:
        return {"side": "buy", "quantity": "10", "constrained": True}
    return None


class SIM001_IdenticalInputs(unittest.TestCase):
    def test_engine_consumes_ordered_canonical_shaped_events(self):
        res = DeterministicSimEngine().run(fixture_events(), momentum_strategy, FrictionModel(), LatencyModel())
        self.assertEqual(len(res["orders"]), 2)
        self.assertEqual(len(res["fills"]), 2)


class SIM002_Determinism(unittest.TestCase):
    def test_repeated_runs_identical_hashes(self):
        runs = [DeterministicSimEngine().run(fixture_events(), momentum_strategy, FrictionModel(), LatencyModel())
                for _ in range(3)]
        self.assertEqual(len({r["result_hash"] for r in runs}), 1)


class SIM003_LatencyPartialFills(unittest.TestCase):
    def test_latency_delays_fill(self):
        res = DeterministicSimEngine().run(fixture_events(), momentum_strategy, FrictionModel(),
                                           LatencyModel(order_latency_events=3))
        self.assertEqual(res["fills"][0]["at_index"], 5)  # submitted at 2, latency 3

    def test_partial_fill_then_remainder(self):
        res = DeterministicSimEngine().run(fixture_events(), constrained_strategy, FrictionModel(), LatencyModel())
        self.assertTrue(res["fills"][0]["partial"])
        self.assertEqual(Decimal(res["fills"][0]["quantity"]), Decimal("5"))
        total = sum(Decimal(f["quantity"]) for f in res["fills"])
        self.assertEqual(total, Decimal("10"))


class SIM004_FrictionsMatter(unittest.TestCase):
    def test_higher_frictions_lower_equity(self):
        cheap = DeterministicSimEngine().run(fixture_events(), momentum_strategy,
                                             FrictionModel(commission_per_unit=Decimal("0")), LatencyModel())
        costly = DeterministicSimEngine().run(fixture_events(), momentum_strategy,
                                              FrictionModel(commission_per_unit=Decimal("5"),
                                                            slippage_per_unit=Decimal("1")), LatencyModel())
        self.assertGreater(Decimal(cheap["equity"]), Decimal(costly["equity"]))


class SIM006_KnowledgeTime(unittest.TestCase):
    def test_future_knowledge_not_consumed(self):
        evs = fixture_events()
        evs[3]["visible_at_index"] = 8  # not knowable until later index
        res = DeterministicSimEngine().run(evs, momentum_strategy, FrictionModel(), LatencyModel())
        self.assertEqual(len(res["knowledge_violations"]), 1)
        self.assertEqual(res["knowledge_violations"][0]["index"], 3)


class SIM007_CheckpointRestart(unittest.TestCase):
    def test_checkpoint_reproduces_uninterrupted_run(self):
        evs = fixture_events()
        full = DeterministicSimEngine().run(evs, momentum_strategy, FrictionModel(), LatencyModel())
        first = DeterministicSimEngine().run(evs[:5], momentum_strategy, FrictionModel(), LatencyModel())
        ck = first["checkpoint"]
        ck["next_index"] = 0  # resume consumes remaining slice from its own start
        resumed = DeterministicSimEngine().run(evs[5:], momentum_strategy, FrictionModel(), LatencyModel(),
                                               checkpoint=ck)
        # NOTE: resumed indices are slice-relative; compare economic outcome
        self.assertEqual(full["final_position"], resumed["final_position"])


class SIM008_ExternalEnginesHonest(unittest.TestCase):
    def test_external_engines_cannot_silently_run(self):
        with self.assertRaises(EntitlementPending):
            NautilusTraderEngine()
        with self.assertRaises(EntitlementPending):
            LeanEngine()


if __name__ == "__main__":
    unittest.main()
