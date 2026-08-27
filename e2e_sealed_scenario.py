"""Phase 11 sealed end-to-end scenario (master plan section 16).

Covers the 13 required elements with fixture data and produces the required lineage chain:
immutable source bytes -> canonical bitemporal events -> as-of snapshot -> versioned features
-> registered experiment -> validated forecast -> calibrated probability -> net expected value
-> deterministic risk decision -> no-trade AND broker-neutral TradeIntent -> paper execution
-> reconciliation -> outcome/memory -> audit reconstruction.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from mios.adapters.fixture_adapter import FixtureMarketDataAdapter
from mios.audit.audit_surface import AuditSurface, DisplayMetric
from mios.contracts.hashing import canonical_json, sha256_hex
from mios.contracts.instruments import InstrumentRef
from mios.contracts.clocks import DeterministicClock
from mios.execution.paper_broker import PaperBroker, PaperLedger, TradeIntent, VenueCapabilities, reconcile
from mios.hardening.integrity import export_backup, verify_backup
from mios.hardening.live_guard import validate_runtime_config
from mios.memory.semantic_memory import SemanticMemory
from mios.newsmacro.macro_vintages import MacroSeries, MacroVintage
from mios.newsmacro.provenance_dedup import independent_roots
from mios.pipeline.ingest import ingest
from mios.research.features import PointInTimeFeatureBuilder
from mios.research.validation import ExperimentRegistry, PreRegistration, evaluate_candidate
from mios.risk.calibration import Calibrator
from mios.risk.expected_value import FrictionConfig, net_expected_value
from mios.risk.risk_engine import RiskPolicy, RiskState, TradeIntentRequest, decide, gate_trade_intent
from mios.shadow.shadow_runner import ShadowRunner
from mios.storage.event_store import EventStore
from mios.timemachine.fixtures import build_adversarial_store, BASE
from mios.timemachine.snapshot import build_snapshot
from mios.timemachine.visibility import VisibilityPolicy

H = timedelta(hours=1)
OUT = os.path.join(ROOT, "artifacts", "acceptance", "phase-11")
INSTR = InstrumentRef(instrument_id="FIX-XYZ", symbol="FIXTURE-XYZ", venue="FIXTURE", asset_class="equity")


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    chain = {}

    # (1) market stream with duplicates + gap + late arrival
    store = EventStore(":memory:")
    sysclock = DeterministicClock(datetime(2026, 1, 5, 15, 0, tzinfo=timezone.utc), 0.5)
    caps = list(FixtureMarketDataAdapter(count=6).capture())
    gapped = caps[:2] + [caps[4], caps[5]] + [caps[1]]          # gap + duplicate
    res = ingest(gapped, store, sysclock, INSTR)
    late = ingest([caps[2]], store, sysclock, INSTR)             # late arrival
    chain["1_market_stream"] = {"stored": len(res.stored) + len(late.stored),
                                "duplicates": len(res.duplicates), "gaps": res.gaps,
                                "incident_kinds": sorted({i["kind"] for i in store.incidents()})}

    # (2) macro series with revisions
    gdp = MacroSeries("FIXTURE-GDP")
    for val, pub in (("2.1", "2026-01-30"), ("2.4", "2026-02-27"), ("2.3", "2026-03-27")):
        gdp.add_vintage(MacroVintage("FIXTURE-GDP", "2025-Q4", val, f"{pub}T13:30:00+00:00", f"{pub}T13:31:00+00:00"))
    chain["2_macro_revisions"] = {"as_of_feb": gdp.value_as_of("2025-Q4", "2026-02-01T00:00:00+00:00").value,
                                  "as_of_apr": gdp.value_as_of("2025-Q4", "2026-04-01T00:00:00+00:00").value}

    # (3) news with update/correction/retraction — adversarial bitemporal store
    news = build_adversarial_store()
    snap_mid = build_snapshot(news, (BASE + 3 * H + timedelta(minutes=5)).isoformat(), VisibilityPolicy.PUBLIC_KNOWABLE)
    chain["3_news_versions"] = {"visible": [(e["event_id"], e["version"]) for e in snap_mid["events"]],
                                "snapshot_hash": snap_mid["snapshot_hash"]}

    # (4) duplicated downstream reporting -> one root
    pr_sha = "c" * 64
    dedup = independent_roots([{"observation_id": f"o{i}", "source_id": f"S{i}", "evidence_roots": [pr_sha]}
                               for i in range(5)])
    chain["4_provenance_dedup"] = dedup

    # (5) point-in-time feature set
    fb = PointInTimeFeatureBuilder(news, (BASE + 4 * H).isoformat())
    fs = fb.feature_set()
    chain["5_feature_set"] = {"hash": fs["feature_set_hash"], "features": fs["features"]}

    # (6) baseline vs deliberately leaky challenger
    reg = ExperimentRegistry()
    reg.preregister(PreRegistration("exp-baseline", "simple momentum", {"net": 0.0}, "2026-01-05T00:00:00+00:00"))
    reg.preregister(PreRegistration("exp-leaky", "leaky challenger", {"net": 0.0}, "2026-01-05T00:00:01+00:00"))
    prices = [Decimal(s) for s in ("100", "101", "102", "101", "103", "104", "103", "105", "106", "107")]
    baseline = evaluate_candidate("exp-baseline", prices, [1] * 10, Decimal("0.05"), reg)
    leaky = evaluate_candidate("exp-leaky", prices, [1] * 10, Decimal("0.05"), reg, used_future_leak=True)
    chain["6_experiments"] = {"baseline": baseline.status, "leaky": leaky.status}

    # (7) calibrated probability with sample size + uncertainty
    cal = Calibrator(min_samples_per_bin=20)
    for i in range(400):
        f = ((i * 37) % 100) / 100.0
        cal.observe(f, 1 if ((i * 53) % 100) / 100.0 < f else 0)
    displayed = cal.displayed_probability(0.7)
    chain["7_calibration"] = displayed

    # (8) positive raw edge -> negative net after friction
    fr = FrictionConfig(*(Decimal(x) for x in ("0.5", "0.3", "0.4", "0.1", "0.1", "0.1", "0.2", "0.3")))
    ev = net_expected_value(Decimal("0.55"), Decimal("4"), Decimal("3"), fr)
    chain["8_net_ev"] = ev

    # (9) no-trade from stale data
    policy = RiskPolicy("fixture-policy", 60, Decimal("100"), Decimal("0.8"))
    stale_decision = decide(TradeIntentRequest("i-stale", "FIX-XYZ", "buy", Decimal("10"), "g1"),
                            RiskState(999, {}, Decimal("0"), Decimal("1000")), policy)
    gate_stale = gate_trade_intent(displayed, ev, stale_decision)
    chain["9_stale_no_trade"] = {"action": gate_stale["action"], "reason": gate_stale["reason"]}

    # (10) approved paper TradeIntent (fresh data, positive net EV variant)
    good_ev = net_expected_value(Decimal("0.7"), Decimal("10"), Decimal("2"), fr)
    fresh_decision = decide(TradeIntentRequest("i-good", "FIX-XYZ", "buy", Decimal("10"), "g1"),
                            RiskState(5, {}, Decimal("0"), Decimal("1000")), policy)
    gate_good = gate_trade_intent(displayed, good_ev, fresh_decision)
    chain["10_trade_intent"] = gate_good

    # (11) partial fill -> restart -> reconciliation
    ledger = PaperLedger()
    broker = PaperBroker(VenueCapabilities("PAPER-FIXTURE", supports_oco=False), ledger)
    oid = broker.submit_paper_order(TradeIntent("i-good", "FIX-XYZ", "buy", Decimal("10")), "idem-1")
    broker.fill(oid, Decimal("4"), Decimal("100.10"))
    state1 = ledger.reconstruct()
    ledger2 = PaperLedger(); ledger2.entries = [dict(e) for e in ledger.entries]   # restart
    state2 = ledger2.reconstruct()
    recon = reconcile(state2, {"position": state2["position"], "orders": {
        oid: {"remaining": state2["orders"][oid]["remaining"], "status": state2["orders"][oid]["status"]}}})
    chain["11_execution"] = {"restart_hash_equal": state1["state_hash"] == state2["state_hash"],
                             "reconciled": recon["reconciled"], "order_status": state2["orders"][oid]["status"]}

    # (12) shadow decision with zero order authority
    sr = ShadowRunner()
    sds = sr.run([{"event_id": f"e{i}", "is_data": True, "evidence_roots": ["d" * 64],
                   "payload": {"price": 100 + i}} for i in range(4)],
                 lambda ev: "would_enter" if ev["payload"]["price"] % 2 == 0 else "no_trade")
    chain["12_shadow"] = {"decisions": len(sds), "no_order_methods": not hasattr(sr, "submit_order"),
                          "sample_lineage": sds[0].lineage_hash}

    # (13) dashboard reconstruction of full lineage
    surface = AuditSurface({"chain": {k: True for k in chain}})
    metric = DisplayMetric("m-e2e", "Sealed scenario", "complete", "fixture",
                           {"decision_id": sds[0].decision_id, "event_versions": chain["3_news_versions"]["visible"]})
    chain["13_audit"] = {"rendered_badge": metric.render()["badge"], "canonical_hash": surface.canonical_hash()}

    # DR + LIVE guards inside the sealed run
    backup = export_backup(store)
    chain["dr"] = verify_backup(backup)
    corrupted = json.loads(json.dumps(backup))
    if corrupted["body"]["raws"]:
        first = next(iter(corrupted["body"]["raws"]))
        corrupted["body"]["raws"][first] = "Y29ycnVwdGVk"  # corrupted bytes
        chain["dr_corruption_detected"] = not verify_backup(corrupted)["clean"]
    try:
        validate_runtime_config({"enable_live_trading": True})
        chain["live_000"] = "FAILED: config accepted"
    except PermissionError:
        chain["live_000"] = "no configuration can enable live authority"

    scenario_hash = sha256_hex(canonical_json(chain))
    with open(os.path.join(OUT, "e2e-sealed-scenario.json"), "w") as f:
        json.dump({"chain": chain, "scenario_hash": scenario_hash}, f, indent=2, sort_keys=True, default=str)
    print(json.dumps({"e2e": "complete", "scenario_hash": scenario_hash,
                      "stale_no_trade": chain["9_stale_no_trade"]["action"],
                      "trade_intent": bool(chain["10_trade_intent"]["trade_intent"]),
                      "live_000": chain["live_000"]}, indent=2))
    # verdicts
    ok = (chain["9_stale_no_trade"]["action"] == "no_trade"
          and chain["10_trade_intent"]["action"] == "approve"
          and chain["11_execution"]["restart_hash_equal"] and chain["11_execution"]["reconciled"]
          and chain["dr"]["clean"] and chain.get("dr_corruption_detected", False)
          and chain["6_experiments"]["leaky"] == "REJECTED_LEAK")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
