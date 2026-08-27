"""Canonical serialization and hashing.

Identical contract values must serialize to identical bytes and hashes (Law 11).
Decimals serialize as exact strings; datetimes serialize as UTC ISO-8601; naive datetimes are rejected.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any


def _canonical_default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return {"__decimal__": format(obj, "f")}
    if isinstance(obj, datetime):
        if obj.tzinfo is None or obj.tzinfo.utcoffset(obj) is None:
            raise ValueError("naive datetime cannot be canonically serialized")
        return {"__datetime_utc__": obj.astimezone(timezone.utc).isoformat()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, bytes):
        return {"__bytes_sha256__": hashlib.sha256(obj).hexdigest()}
    if hasattr(obj, "to_canonical_dict"):
        return obj.to_canonical_dict()
    raise TypeError(f"type {type(obj).__name__} has no canonical serialization")


def canonical_json(data: Any) -> bytes:
    """Deterministic canonical JSON: sorted keys, minimal separators, UTF-8."""
    return json.dumps(
        data, default=_canonical_default, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contract_hash(data: Any) -> str:
    return sha256_hex(canonical_json(data))
