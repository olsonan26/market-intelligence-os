"""Provider-neutral market-data port (Law 8). Domain code depends on this, never on providers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

from ..contracts.timestamps import PointInTimeTimestamp


@dataclass(frozen=True)
class RawCapture:
    """Original bytes captured from a source, before any normalization (Law 5)."""

    source_id: str
    provider: str
    raw_bytes: bytes
    received_at: PointInTimeTimestamp
    content_type: str
    source_sequence: Optional[int] = None
    is_test_fixture: bool = False


class MarketDataPort(Protocol):
    """Any market-data adapter implements this and nothing leaks provider models upward."""

    def capture(self) -> Iterable[RawCapture]:
        ...
