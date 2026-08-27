"""Empirical probability calibration (Phase 7: PR-001..PR-003).

Displayed probabilities are EMPIRICAL, never raw model confidence (constitutional law 14).
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class CalibrationBin:
    lower: float
    upper: float
    forecasts: int
    realized_rate: Optional[float]
    uncertainty: Optional[float]     # standard error of realized rate


class Calibrator:
    """Bins historical (forecast, outcome) pairs and answers with EMPIRICAL frequencies."""

    def __init__(self, n_bins: int = 10, min_samples_per_bin: int = 20, tolerance: float = 0.10) -> None:
        self._n = n_bins
        self._min = min_samples_per_bin
        self._tol = tolerance
        self._pairs: List[Tuple[float, int]] = []
        self._reference_mean: Optional[float] = None

    def observe(self, forecast: float, outcome: int) -> None:
        if not (0.0 <= forecast <= 1.0) or outcome not in (0, 1):
            raise ValueError("forecast in [0,1], outcome in {0,1}")
        self._pairs.append((forecast, outcome))
        if self._reference_mean is None and len(self._pairs) >= 100:
            self._reference_mean = sum(f for f, _ in self._pairs) / len(self._pairs)

    def bins(self) -> List[CalibrationBin]:
        out = []
        for k in range(self._n):
            lo, hi = k / self._n, (k + 1) / self._n
            hits = [(f, o) for f, o in self._pairs if lo <= f < hi or (k == self._n - 1 and f == 1.0)]
            if len(hits) >= self._min:
                rate = sum(o for _, o in hits) / len(hits)
                se = sqrt(rate * (1 - rate) / len(hits)) if len(hits) else None
                out.append(CalibrationBin(lo, hi, len(hits), round(rate, 4), round(se, 4) if se is not None else None))
            else:
                out.append(CalibrationBin(lo, hi, len(hits), None, None))
        return out

    def displayed_probability(self, raw_model_confidence: float) -> dict:
        """Returns the empirical calibrated probability WITH sample size and uncertainty (PR-002),
        or abstains when evidence is insufficient."""
        k = min(int(raw_model_confidence * self._n), self._n - 1)
        b = self.bins()[k]
        if b.realized_rate is None:
            return {"display": None, "abstain": True,
                    "reason": f"bin [{b.lower},{b.upper}) has only {b.forecasts} samples (<{self._min})",
                    "raw_confidence_never_displayed": True}
        return {"display": b.realized_rate, "sample_size": b.forecasts, "uncertainty": b.uncertainty,
                "abstain": False, "raw_confidence_never_displayed": True}

    def drift_check(self, recent: Sequence[float]) -> dict:
        """PR-003: distribution shift triggers downgrade/abstention/recalibration policy."""
        if self._reference_mean is None or not recent:
            return {"shift_detected": False, "action": "none"}
        recent_mean = sum(recent) / len(recent)
        if abs(recent_mean - self._reference_mean) > self._tol:
            return {"shift_detected": True, "action": "abstain_and_recalibrate",
                    "reference_mean": round(self._reference_mean, 4), "recent_mean": round(recent_mean, 4)}
        return {"shift_detected": False, "action": "none"}
