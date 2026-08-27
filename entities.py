"""Versioned, auditable entity->instrument mappings with confidence (NEWS-008)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EntityMapping:
    entity: str
    instrument_id: str
    confidence: float
    version: int
    valid_from: str
    mapped_by: str          # audit trail


class EntityMapper:
    def __init__(self) -> None:
        self._mappings: List[EntityMapping] = []

    def add(self, m: EntityMapping) -> None:
        prior = [x for x in self._mappings if x.entity == m.entity]
        expected_version = len(prior) + 1
        if m.version != expected_version:
            raise ValueError(f"entity mapping versions are sequential; expected {expected_version}")
        self._mappings.append(m)  # append-only, fully auditable

    def resolve(self, entity: str, as_of: str) -> Optional[EntityMapping]:
        candidates = [x for x in self._mappings if x.entity == entity and x.valid_from <= as_of]
        return max(candidates, key=lambda x: x.version) if candidates else None

    def history(self, entity: str) -> List[EntityMapping]:
        return [x for x in self._mappings if x.entity == entity]
