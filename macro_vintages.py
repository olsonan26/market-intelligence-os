"""ALFRED-style macro series vintages: each revision knowable only from its own vintage date (NEWS-005)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class MacroVintage:
    series_id: str
    observation_period: str      # e.g. "2025-Q4"
    value: str
    vintage_published_at: str    # when THIS revision became public
    ingested_at: str             # when THIS system captured it


class MacroSeries:
    def __init__(self, series_id: str) -> None:
        self.series_id = series_id
        self._vintages: List[MacroVintage] = []

    def add_vintage(self, v: MacroVintage) -> None:
        self._vintages.append(v)  # append-only

    def value_as_of(self, period: str, cutoff_utc: str, policy: str = "public_knowable") -> Optional[MacroVintage]:
        clock = (lambda v: v.vintage_published_at) if policy == "public_knowable" else (lambda v: v.ingested_at)
        candidates = [v for v in self._vintages if v.observation_period == period and clock(v) <= cutoff_utc]
        if not candidates:
            return None
        return max(candidates, key=lambda v: clock(v))  # latest vintage knowable at cutoff
