"""Canonical event contract (provider-neutral, Law 8)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Tuple

from .clocks import FourClocks
from .hashing import canonical_json, sha256_hex
from .instruments import InstrumentRef
from .licensing import LicensePolicy
from .schema_registry import check_schema


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    provider: str
    source_event_id: Optional[str] = None
    source_sequence: Optional[int] = None

    def to_canonical_dict(self) -> dict:
        return {
            "schema": "mios.source_ref",
            "source_id": self.source_id,
            "provider": self.provider,
            "source_event_id": self.source_event_id,
            "source_sequence": self.source_sequence,
        }


@dataclass(frozen=True)
class CanonicalEvent:
    event_id: str
    schema_name: str
    schema_version: str
    source: SourceRef
    clocks: FourClocks
    payload: Mapping[str, Any]
    raw_payload_sha256: str
    license_policy: LicensePolicy
    evidence_roots: Tuple[str, ...]
    instrument: Optional[InstrumentRef] = None
    is_test_fixture: bool = False

    def __post_init__(self) -> None:
        check_schema(self.schema_name, self.schema_version)
        if len(self.raw_payload_sha256) != 64:
            raise ValueError("raw before normalized: raw_payload_sha256 must be a sha-256 of original bytes")
        if not self.evidence_roots:
            raise ValueError("provenance before confidence: at least one evidence root is required")

    def to_canonical_dict(self) -> dict:
        return {
            "schema": self.schema_name,
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "source": self.source.to_canonical_dict(),
            "clocks": self.clocks.to_canonical_dict(),
            "payload": dict(self.payload),
            "raw_payload_sha256": self.raw_payload_sha256,
            "license_policy": self.license_policy.to_canonical_dict(),
            "evidence_roots": list(self.evidence_roots),
            "instrument": self.instrument.to_canonical_dict() if self.instrument else None,
            "is_test_fixture": self.is_test_fixture,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json(self.to_canonical_dict())

    def content_hash(self) -> str:
        return sha256_hex(self.canonical_bytes())
