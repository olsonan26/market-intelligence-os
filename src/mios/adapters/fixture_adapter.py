"""Deterministic fixture adapter.

Every record is explicitly labeled as a test fixture and is impossible to confuse with
real market data: fixture source ids are prefixed FIXTURE-, payloads carry
"fixture": true and a NOT-REAL-MARKET-DATA banner, and is_test_fixture=True.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable, List

from ..contracts.clocks import DeterministicClock
from ..contracts.timestamps import PointInTimeTimestamp, TimePrecision
from .port import RawCapture

FIXTURE_SOURCE_ID = "FIXTURE-MARKETDATA-V1"
FIXTURE_BANNER = "FIXTURE-TEST-DATA-NOT-REAL-MARKET-DATA"


class FixtureMarketDataAdapter:
    """Emits a deterministic, seeded sequence of labeled fixture captures."""

    def __init__(self, start: datetime | None = None, count: int = 5) -> None:
        self._clock = DeterministicClock(start or datetime(2026, 1, 5, 14, 30, tzinfo=timezone.utc))
        self._count = count

    def capture(self) -> Iterable[RawCapture]:
        captures: List[RawCapture] = []
        price_cents = 10000
        for i in range(self._count):
            instant = self._clock.now()
            price_cents += (7 * (i + 1)) % 13 - 6  # deterministic, seedless arithmetic walk
            payload = {
                "fixture": True,
                "banner": FIXTURE_BANNER,
                "seq": i,
                "symbol": "FIXTURE-XYZ",
                "price": f"{price_cents // 100}.{price_cents % 100:02d}",
                "ts": instant.isoformat(),
            }
            raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            captures.append(
                RawCapture(
                    source_id=FIXTURE_SOURCE_ID,
                    provider="fixture",
                    raw_bytes=raw,
                    received_at=PointInTimeTimestamp(
                        utc=instant, precision=TimePrecision.SECOND, raw_text=instant.isoformat(),
                        source_timezone="UTC",
                    ),
                    content_type="application/json",
                    source_sequence=i,
                    is_test_fixture=True,
                )
            )
        return captures
