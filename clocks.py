"""Four-clock contract and injectable clocks.

Laws: four distinct clocks (2); knowledge time never fabricated (3); deterministic replay (11).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from .timestamps import NaiveTimestampError, PointInTimeTimestamp


class KnowledgeTimeFabricationError(ValueError):
    """ingested_at would be fabricated rather than genuinely captured (Law 3)."""


@dataclass(frozen=True)
class FourClocks:
    """event_time / published_at / ingested_at / system_time, all semantically distinct."""

    event_time: PointInTimeTimestamp
    ingested_at: PointInTimeTimestamp
    system_time: PointInTimeTimestamp
    published_at: Optional[PointInTimeTimestamp] = None
    ingested_at_genuine_capture: bool = True

    def __post_init__(self) -> None:
        if not self.ingested_at_genuine_capture:
            raise KnowledgeTimeFabricationError(
                "ingested_at may only be set to an instant at which this system genuinely captured the item; "
                "archive publication time must not be copied into receipt time"
            )

    def to_canonical_dict(self) -> dict:
        return {
            "schema": "mios.clocks",
            "event_time": self.event_time.to_canonical_dict(),
            "published_at": self.published_at.to_canonical_dict() if self.published_at else None,
            "ingested_at": self.ingested_at.to_canonical_dict(),
            "system_time": self.system_time.to_canonical_dict(),
        }


class DeterministicClock:
    """Injectable clock producing a reproducible sequence of UTC instants (tests / replay)."""

    def __init__(self, start: datetime, step_seconds: float = 1.0) -> None:
        if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:
            raise NaiveTimestampError("DeterministicClock requires a timezone-aware start instant")
        self._current = start.astimezone(timezone.utc)
        self._step = timedelta(seconds=step_seconds)

    def now(self) -> datetime:
        value = self._current
        self._current = self._current + self._step
        return value
