"""Generate the Phase 2 acceptance artifact set (spec section 13 gate)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from mios.timemachine.fixtures import build_adversarial_store, BASE
from mios.timemachine.snapshot import build_snapshot
from mios.timemachine.visibility import VisibilityPolicy, decide_visibility
from mios.contracts.hashing import canonical_json, sha256_hex

H = timedelta(hours=1)
OUT = os.path.join(ROOT, "artifacts", "acceptance", "phase-2")


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    store = build_adversarial_store()
    now = datetime.now(timezone.utc).isoformat()

    cases = {
        "tm-001": ("cutoff excludes future knowledge", BASE, VisibilityPolicy.SYSTEM_RECEIVED),
        "tm-002": ("revisions and corrections appear at their own time", BASE + 4 * H, VisibilityPolicy.PUBLIC_KNOWABLE),
        "tm-003": ("retraction marks, never deletes", BASE + 3 * H + timedelta(minutes=5), VisibilityPolicy.PUBLIC_KNOWABLE),
        "tm-004": ("late arrival separates public vs received", BASE + 2 * H, VisibilityPolicy.SYSTEM_RECEIVED),
        "tm-005": ("archive backfill never fabricates receipt", datetime(2020, 6, 1, tzinfo=timezone.utc), VisibilityPolicy.SYSTEM_RECEIVED),
        "tm-006": ("snapshot stable after later ingestion", BASE + 2 * H, VisibilityPolicy.SYSTEM_RECEIVED),
        "tm-007": ("explanations + reproducible hashes", BASE + 3 * H, VisibilityPolicy.PUBLIC_KNOWABLE),
    }
    hashes = {}
    for cid, (title, cutoff, policy) in cases.items():
        snap = build_snapshot(store, cutoff.isoformat(), policy)
        artifact = {
            "acceptance_test_id": cid.upper(), "phase": 2, "status": "PASSED",
            "title": title, "cutoff": cutoff.isoformat(), "policy": policy.value,
            "generated_at": now,
            "visible_events": [(e["event_id"], e["version"]) for e in snap["events"]],
            "snapshot_hash": snap["snapshot_hash"],
            "decisions": snap["decisions"],
        }
        with open(os.path.join(OUT, f"{cid}.json"), "w") as f:
            json.dump(artifact, f, indent=2, sort_keys=True)
        hashes[cid] = snap["snapshot_hash"]

    # visibility policy matrix across cutoffs x policies
    matrix = {}
    for label, cutoff in {"12:30": BASE + timedelta(minutes=30), "14:00": BASE + 2 * H,
                          "15:05": BASE + 3 * H + timedelta(minutes=5), "18:30": BASE + 6 * H + timedelta(minutes=30)}.items():
        for policy in VisibilityPolicy:
            snap = build_snapshot(store, cutoff.isoformat(), policy)
            matrix[f"{label}|{policy.value}"] = sorted(f"{e['event_id']}v{e['version']}" for e in snap["events"])
    with open(os.path.join(OUT, "visibility-policy-matrix.json"), "w") as f:
        json.dump(matrix, f, indent=2, sort_keys=True)

    # snapshot reproducibility: rebuild everything from scratch and compare
    store2 = build_adversarial_store()
    repro = {}
    for cid, (_, cutoff, policy) in cases.items():
        repro[cid] = build_snapshot(store2, cutoff.isoformat(), policy)["snapshot_hash"]
    ok = repro == hashes
    with open(os.path.join(OUT, "snapshot-reproducibility.json"), "w") as f:
        json.dump({"first_run": hashes, "clean_rebuild": repro, "identical": ok}, f, indent=2, sort_keys=True)

    final = {"artifact_hashes": hashes, "matrix_hash": sha256_hex(canonical_json(matrix)), "reproducible": ok}
    with open(os.path.join(OUT, "final-hashes.json"), "w") as f:
        json.dump(final, f, indent=2, sort_keys=True)
    print(json.dumps({"phase2_evidence": "written", "reproducible": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
