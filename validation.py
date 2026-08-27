"""Governed model arena: purged splits, cost-aware evaluation, pre-registration (Phase 4)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from ..contracts.hashing import canonical_json, sha256_hex


@dataclass(frozen=True)
class PreRegistration:
    experiment_id: str
    hypothesis: str
    promotion_thresholds: Dict[str, float]
    registered_at: str
    hypothesis_test_count: int = 1  # VAL-004: repeated testing recorded


class ExperimentRegistry:
    """Append-only registry: pre-registrations, immutable results, negative results retained."""

    def __init__(self) -> None:
        self._prereg: Dict[str, PreRegistration] = {}
        self._results: List[dict] = []
        self._test_counts: Dict[str, int] = {}

    def preregister(self, reg: PreRegistration) -> None:
        if reg.experiment_id in self._prereg:
            raise ValueError("experiment id already registered; registrations are immutable")
        self._prereg[reg.experiment_id] = reg
        self._test_counts[reg.hypothesis] = self._test_counts.get(reg.hypothesis, 0) + 1

    def hypothesis_attempts(self, hypothesis: str) -> int:
        return self._test_counts.get(hypothesis, 0)

    def record_result(self, experiment_id: str, result: dict) -> dict:
        if experiment_id not in self._prereg:
            raise ValueError("results may only be recorded for pre-registered experiments")
        attempts = self.hypothesis_attempts(self._prereg[experiment_id].hypothesis)
        # simple Bonferroni-style explicit bound on repeated testing (VAL-004)
        adjusted_alpha = 0.05 / max(1, attempts)
        entry = {
            "experiment_id": experiment_id, "result": result,
            "hypothesis_attempts": attempts, "adjusted_alpha": adjusted_alpha,
            "result_hash": sha256_hex(canonical_json(result)),
        }
        self._results.append(entry)  # negative results stay forever
        return entry

    def all_results(self) -> List[dict]:
        return list(self._results)


def purged_chronological_splits(n: int, n_folds: int, label_horizon: int) -> List[Tuple[range, range]]:
    """Chronological folds with purge gap = label_horizon so overlapping labels can't contaminate (VAL-002)."""
    folds = []
    fold_size = n // n_folds
    for k in range(1, n_folds):
        train_end = k * fold_size - label_horizon  # purge
        test_start = k * fold_size
        test_end = min(n, (k + 1) * fold_size)
        if train_end <= 0:
            continue
        folds.append((range(0, train_end), range(test_start, test_end)))
    return folds


@dataclass
class EvaluationOutcome:
    experiment_id: str
    gross_return: Decimal
    net_return: Decimal
    accepted: bool
    status: str
    reasons: List[str]

    def to_canonical_dict(self) -> dict:
        return {"experiment_id": self.experiment_id, "gross_return": str(self.gross_return),
                "net_return": str(self.net_return), "accepted": self.accepted,
                "status": self.status, "reasons": self.reasons}


def evaluate_candidate(experiment_id: str, prices: Sequence[Decimal], signals: Sequence[int],
                       cost_per_trade: Decimal, registry: ExperimentRegistry,
                       baseline_net: Decimal = Decimal("0"),
                       used_future_leak: bool = False,
                       robustness_shift_signals: Optional[Sequence[int]] = None) -> EvaluationOutcome:
    """Cost-aware, leak-rejecting, baseline-compared evaluation. No-trade is first-class (VAL-009)."""
    reasons: List[str] = []
    if used_future_leak:
        out = EvaluationOutcome(experiment_id, Decimal("0"), Decimal("0"), False, "REJECTED_LEAK",
                                ["feature set declared future leakage (VAL-001)"])
        registry.record_result(experiment_id, out.to_canonical_dict())
        return out

    def run(sig: Sequence[int]) -> Tuple[Decimal, Decimal, int]:
        gross = Decimal("0"); trades = 0; pos = 0
        for i in range(1, len(prices)):
            if sig[i - 1] != pos:
                trades += abs(sig[i - 1] - pos); pos = sig[i - 1]
            gross += (prices[i] - prices[i - 1]) * pos
        net = gross - cost_per_trade * trades
        return gross, net, trades

    gross, net, trades = run(signals)
    accepted = True; status = "ELIGIBLE"
    if net <= baseline_net:
        accepted = False; status = "NOT_ELIGIBLE"
        reasons.append(f"net return {net} does not beat no-trade baseline {baseline_net} after costs (VAL-003/009)")
    if robustness_shift_signals is not None:
        _, shifted_net, _ = run(robustness_shift_signals)
        if shifted_net <= 0 or shifted_net < net * Decimal("0.5"):
            accepted = False; status = "NOT_ELIGIBLE"
            reasons.append("fails adjacent-period/perturbation robustness (VAL-006)")
    out = EvaluationOutcome(experiment_id, gross, net, accepted, status, reasons or ["passed all gates"])
    registry.record_result(experiment_id, out.to_canonical_dict())
    return out


class ChampionChallengerRegistry:
    """Locked promotion thresholds (VAL-007)."""

    def __init__(self, thresholds: Dict[str, float]) -> None:
        self._thresholds = dict(thresholds)
        self.champion: Optional[str] = None

    def consider(self, candidate_id: str, metrics: Dict[str, float]) -> str:
        for name, minimum in self._thresholds.items():
            if metrics.get(name, float("-inf")) < minimum:
                return "NOT_ELIGIBLE"
        self.champion = candidate_id
        return "PROMOTED"
