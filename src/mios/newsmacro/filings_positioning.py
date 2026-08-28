"""Filing visibility (SEC acceptance/dissemination clocks) and COT-style publication lag (NEWS-004/006)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Filing:
    filing_id: str
    period_end: str
    accepted_at: str        # SEC acceptance timestamp
    disseminated_at: str    # public dissemination timestamp


def filing_visible(f: Filing, cutoff_utc: str) -> bool:
    """Dissemination governs public visibility, never the fiscal period end."""
    return f.disseminated_at <= cutoff_utc


@dataclass(frozen=True)
class PositioningObservation:
    report_id: str
    observed_on: str        # Tuesday observation date
    published_at: str       # Friday publication


def positioning_visible(p: PositioningObservation, cutoff_utc: str) -> bool:
    """Tuesday observations are invisible until Friday publication (NEWS-006)."""
    return p.published_at <= cutoff_utc
