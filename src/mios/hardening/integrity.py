"""Backup/restore integrity and corruption quarantine (DR-001/002)."""
from __future__ import annotations

import base64
import hashlib
import json
from typing import Dict, List, Tuple

from ..storage.event_store import EventStore


def export_backup(store: EventStore) -> dict:
    """Deterministic logical backup of the canonical store."""
    events = [dict(r) for r in store.all_events()]
    incidents = [dict(r) for r in store.incidents()]
    raws = {}
    for e in events:
        raw = store.load_raw_bytes(e["raw_sha256"])
        if raw is not None:
            raws[e["raw_sha256"]] = base64.b64encode(raw).decode("ascii")
    body = {"events": events, "incidents": incidents, "raws": raws}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"body": body, "backup_hash": digest}


def verify_backup(backup: dict) -> dict:
    """Detect and quarantine corrupted raw objects (DR-002)."""
    quarantined: List[str] = []
    for sha, b64 in backup["body"]["raws"].items():
        raw = base64.b64decode(b64)
        if hashlib.sha256(raw).hexdigest() != sha:
            quarantined.append(sha)
    return {"clean": not quarantined, "quarantined": quarantined}
