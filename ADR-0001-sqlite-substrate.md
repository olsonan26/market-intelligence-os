# ADR-0001: SQLite as the canonical store in this build environment

**Status:** Accepted
**Decision changed:** Phase 0-2 spec names PostgreSQL for canonical metadata and append-only event records.
**Forcing evidence:** The build environment has no PostgreSQL server, no Docker, and no network package
installation (`psql`, `pg_ctl`, `docker` absent; pip installs blocked by network policy). Recorded in
`artifacts/acceptance/preflight/manifest.json`.
**Decision:** Implement the storage layer behind a neutral `EventStore` port. Provide a SQLite adapter that
enforces the identical append-only, bitemporal, and uniqueness contracts (triggers reject UPDATE/DELETE on
evidence tables). The schema DDL is written to be PostgreSQL-portable; a `postgres_notes.sql` file records the
type mappings required when a PostgreSQL environment is available.
**Affected invariants:** none weakened - append-only, four clocks, raw-before-normalized, uniqueness, and
deterministic replay are all enforced in the SQLite adapter and covered by the same contract tests.
**Migration consequences:** swapping to PostgreSQL requires only a new adapter implementing `EventStore` and
running the portable DDL; contract tests are adapter-parameterized.
**Regression tests:** `tests/test_store_append_only.py` runs the full contract suite against the adapter.
**Rollback path:** delete the SQLite adapter; the port and tests remain.
