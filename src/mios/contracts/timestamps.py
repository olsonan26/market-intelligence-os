"""Point-in-time timestamp contract.

Laws: UTC internally, naive rejected (9); raw text + source timezone preserved (9);
precision never invented (10).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TimePrecision(Enum):
    SECOND = "second"
    MILLISECOND = "millisecond"
    MICROSECOND = "microsecond"
    NANOSECOND = "nanosecond"


PRECISION_RANK = {
    TimePrecision.SECOND: 0,
    TimePrecision.MILLISECOND: 1,
    TimePrecision.MICROSECOND: 2,
    TimePrecision.NANOSECOND: 3,
}


class NaiveTimestampError(ValueError):
    """A timezone-naive datetime attempted to enter the system."""


class PrecisionInventionError(ValueError):
    """A timestamp claims finer precision than its source supplied."""


@dataclass(frozen=True)
class PointInTimeTimestamp:
    """A UTC instant that preserves its original source representation."""

    utc: datetime
    precision: TimePrecision
    raw_text: Optional[str] = None
    source_timezone: Optional[str] = None

    def __post_init__(self) -> None:
        if self.utc.tzinfo is None or self.utc.tzinfo.utcoffset(self.utc) is None:
            raise NaiveTimestampError("naive datetime rejected: all timestamps must be timezone-aware")
        object.__setattr__(self, "utc", self.utc.astimezone(timezone.utc))
        if self.precision is TimePrecision.SECOND and self.utc.microsecond != 0:
            raise PrecisionInventionError("second-resolution source cannot carry sub-second digits")
        if self.precision is TimePrecision.MILLISECOND and self.utc.microsecond % 1000 != 0:
            raise PrecisionInventionError("millisecond-resolution source cannot carry microsecond digits")

    def to_canonical_dict(self) -> dict:
        return {
            "schema": "mios.timestamp",
            "utc": self.utc.isoformat(),
            "precision": self.precision.value,
            "raw_text": self.raw_text,
            "source_timezone": self.source_timezone,
        }
