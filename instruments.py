"""Instrument identity contract."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentRef:
    instrument_id: str
    symbol: str
    venue: str
    asset_class: str

    def to_canonical_dict(self) -> dict:
        return {
            "schema": "mios.instrument",
            "instrument_id": self.instrument_id,
            "symbol": self.symbol,
            "venue": self.venue,
            "asset_class": self.asset_class,
        }
