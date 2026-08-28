"""Schema version registry. Version mismatches fail explicitly."""
from __future__ import annotations

SCHEMA_VERSIONS = {
    "mios.timestamp": "1.0.0",
    "mios.clocks": "1.0.0",
    "mios.license_policy": "1.0.0",
    "mios.instrument": "1.0.0",
    "mios.source_ref": "1.0.0",
    "mios.evidence_root": "1.0.0",
    "mios.provenance_edge": "1.0.0",
    "mios.canonical_event": "1.0.0",
    "mios.raw_capture": "1.0.0",
}


class SchemaVersionMismatch(ValueError):
    """Schema name unknown or version does not match the registry."""


def check_schema(name: str, version: str) -> None:
    expected = SCHEMA_VERSIONS.get(name)
    if expected is None:
        raise SchemaVersionMismatch(f"unknown schema '{name}'")
    if expected != version:
        raise SchemaVersionMismatch(f"schema '{name}' version mismatch: expected {expected}, got {version}")
