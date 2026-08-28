-- Canonical bitemporal store (portable DDL; see ADR-0001 and postgres_notes.sql)
CREATE TABLE IF NOT EXISTS raw_payloads (
    raw_sha256      TEXT PRIMARY KEY,
    source_id       TEXT NOT NULL,
    provider        TEXT NOT NULL,
    content_type    TEXT NOT NULL,
    raw_bytes_b64   TEXT NOT NULL,
    received_at_utc TEXT NOT NULL,
    received_prec   TEXT NOT NULL,
    received_raw    TEXT,
    source_tz       TEXT,
    source_sequence INTEGER,
    is_test_fixture INTEGER NOT NULL DEFAULT 0,
    system_time_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical_events (
    row_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id         TEXT NOT NULL,
    version          INTEGER NOT NULL,
    version_kind     TEXT NOT NULL,          -- original | revision | correction | retraction
    schema_name      TEXT NOT NULL,
    schema_version   TEXT NOT NULL,
    source_id        TEXT NOT NULL,
    provider         TEXT NOT NULL,
    source_event_id  TEXT,
    source_sequence  INTEGER,
    instrument_id    TEXT,
    event_time_utc   TEXT NOT NULL,
    published_at_utc TEXT,
    ingested_at_utc  TEXT NOT NULL,
    system_time_utc  TEXT NOT NULL,
    payload_json     TEXT NOT NULL,
    raw_sha256       TEXT NOT NULL REFERENCES raw_payloads(raw_sha256),
    license_json     TEXT NOT NULL,
    evidence_roots   TEXT NOT NULL,
    content_hash     TEXT NOT NULL,
    is_test_fixture  INTEGER NOT NULL DEFAULT 0,
    UNIQUE(event_id, version),
    UNIQUE(source_id, source_event_id, version)
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    kind            TEXT NOT NULL,   -- duplicate | gap | invalid_schema | clock_inversion | rejected_payload
    source_id       TEXT NOT NULL,
    detail_json     TEXT NOT NULL,
    raw_sha256      TEXT,
    system_time_utc TEXT NOT NULL
);

-- Append-only enforcement
CREATE TRIGGER IF NOT EXISTS raw_no_update BEFORE UPDATE ON raw_payloads
BEGIN SELECT RAISE(ABORT, 'append-only: raw_payloads may not be updated'); END;
CREATE TRIGGER IF NOT EXISTS raw_no_delete BEFORE DELETE ON raw_payloads
BEGIN SELECT RAISE(ABORT, 'append-only: raw_payloads may not be deleted'); END;
CREATE TRIGGER IF NOT EXISTS evt_no_update BEFORE UPDATE ON canonical_events
BEGIN SELECT RAISE(ABORT, 'append-only: canonical_events may not be updated'); END;
CREATE TRIGGER IF NOT EXISTS evt_no_delete BEFORE DELETE ON canonical_events
BEGIN SELECT RAISE(ABORT, 'append-only: canonical_events may not be deleted'); END;
CREATE TRIGGER IF NOT EXISTS inc_no_update BEFORE UPDATE ON incidents
BEGIN SELECT RAISE(ABORT, 'append-only: incidents may not be updated'); END;
CREATE TRIGGER IF NOT EXISTS inc_no_delete BEFORE DELETE ON incidents
BEGIN SELECT RAISE(ABORT, 'append-only: incidents may not be deleted'); END;
