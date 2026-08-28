"""Provenance contracts: evidence roots and edges (Laws 4/6). Append-only by construction."""
from __future__ import annotations

from dataclasses import dataclass

from .timestamps import PointInTimeTimestamp


@dataclass(frozen=True)
class EvidenceRoot:
    """Immutable original bytes, identified by their SHA-256, captured at a genuine instant."""

    raw_payload_sha256: str
    source_id: str
    captured_at: PointInTimeTimestamp

    def __post_init__(self) -> None:
        if len(self.raw_payload_sha256) != 64:
            raise ValueError("evidence root must reference a sha-256 hex digest of original bytes")

    def to_canonical_dict(self) -> dict:
        return {
            "schema": "mios.evidence_root",
            "raw_payload_sha256": self.raw_payload_sha256,
            "source_id": self.source_id,
            "captured_at": self.captured_at.to_canonical_dict(),
        }


@dataclass(frozen=True)
class ProvenanceEdge:
    """Derived record -> evidence root linkage."""

    derived_id: str
    evidence_root_sha256: str
    relation: str

    def to_canonical_dict(self) -> dict:
        return {
            "schema": "mios.provenance_edge",
            "derived_id": self.derived_id,
            "evidence_root_sha256": self.evidence_root_sha256,
            "relation": self.relation,
        }
