# MARKET INTELLIGENCE OS
## Master Build Prompt — Phases 0–2

**Version:** 1.0

**Authority:** Architecture Lock V1

**Repository:** `olsonan26/market-intelligence-os`

**Status:** Approved construction specification for the foundation only

**Hard stop:** Do not implement Phase 3 or later

---

## 1. Your assignment

You are the principal systems engineer responsible for constructing the first three phases of a point-in-time-correct, multi-market Market Intelligence and Experimentation Operating System.

You are **not** building a trading bot, signal dashboard, chart-reading chatbot, strategy showcase, or profit promise. You are building the truth substrate that later research, models, agents, risk controls, simulations, and broker adapters must depend upon.

The first release must prove that the system can:

1. preserve original external evidence without mutation;
2. distinguish when something happened, when it was published, when this system received it, and when the database recorded it;
3. reconstruct exactly what was knowable at a historical cutoff;
4. preserve revisions, corrections, retractions, late arrivals, source sequence, provenance, and license restrictions;
5. replay the same event log deterministically; and
6. produce stored, reproducible acceptance evidence rather than claiming completion from screenshots or passing unit-test counts.

Build only:

- **Phase 0 — Constitution and canonical contracts**
- **Phase 1 — One narrow market-data vertical slice**
- **Phase 2 — The point-in-time Time Machine**

At the end of Phase 2, stop. Do not begin research engines, AI agents, backtesting frameworks, broker execution, dashboards, or live trading.

---

## 2. Authority hierarchy

When instructions conflict, obey this order:

1. security, law, data licensing, and explicit human authorization;
2. Architecture Lock V1;
3. this Phase 0–2 Master Build Prompt;
4. accepted Architecture Decision Records (ADRs);
5. implementation tickets and code comments;
6. convenience, framework defaults, and personal preference.

Any material deviation requires a written ADR that states:

- the decision being changed;
- the evidence that forced the change;
- affected invariants and schemas;
- migration consequences;
- new or modified regression tests; and
- the rollback path.

Do not silently reinterpret a requirement.

---

## 3. Preflight gate

Before creating application code, verify and record:

- the repository is private;
- the default branch is protected or the intended PR workflow is documented;
- no live brokerage credentials exist;
- no paid market-data credentials are committed;
- no secrets are stored in tracked files, examples, fixtures, logs, or test artifacts;
- `.env*`, credential files, local data volumes, raw licensed payloads, and generated acceptance artifacts have appropriate ignore and retention policies;
- the repository contains no inherited trading-bot code or unverifiable performance claims; and
- the system has no path capable of submitting a live order.

If the repository is public, stop before adding proprietary research, credentials, provider payloads, or implementation details that should remain private. Report the blocker plainly.

Record the successful preflight as `artifacts/acceptance/preflight/manifest.json`.

---

## 4. Non-negotiable laws

Implement these as enforceable contracts and tests, not slogans.

1. **Point-in-time truth.** A replay may see only records permitted by the selected historical visibility policy at or before its cutoff.
2. **Four clocks where applicable.** Preserve `event_time`, `published_at`, `ingested_at`, and `system_time`. Exchange and provider-first-seen clocks are additional clocks, not substitutes.
3. **Never fabricate knowledge time.** Do not copy a historical `published_at` into `ingested_at` unless the system genuinely captured the item at that instant.
4. **Append-only evidence.** Raw payloads, event versions, corrections, retractions, sequence incidents, and provenance edges are never overwritten.
5. **Raw before normalized.** Store and hash original bytes before canonical transformation.
6. **Provenance before confidence.** Derived records must point back to independent evidence roots.
7. **Rights are data.** Every payload and derived record carries a machine-enforceable license policy.
8. **Provider neutrality.** Domain code consumes canonical contracts and never imports provider payload models directly.
9. **UTC internally.** Reject naive timestamps. Preserve the source timezone and raw timestamp text when supplied.
10. **Precision is not invented.** Never promote second-resolution source data to nanosecond certainty.
11. **Deterministic replay.** Identical event log, code, configuration, snapshot, and seed must produce identical ordered outputs and hashes.
12. **Failures become evidence.** Gaps, duplicates, invalid schemas, clock inversions, and rejected payloads are stored as incidents.
13. **No fake completion.** A phase is incomplete until every required acceptance case produces stored evidence.
14. **No live authority.** Phases 0–2 may not import broker SDKs, create order routes, or accept live-trading credentials.

---

## 5. Scope boundaries

### 5.1 Required now

- project constitution and ADR process;
- reproducible Python workspace and pinned dependency lock;
- typed canonical event contracts;
- clock, source, provenance, instrument, license, and schema-version contracts;
- immutable raw payload storage;
- PostgreSQL canonical metadata and append-only event records;
- one provider-neutral adapter interface;
- one deterministic fixture adapter;
- one approved market-data adapter or explicitly documented entitlement blocker;
- one liquid instrument;
- capture, normalization, deduplication, sequence validation, quarantine, and replay;
- public-information and system-realistic historical views;
- revision-aware macro and news fixtures;
- snapshot manifests and artifact hashes;
- CLI or minimal internal API for capture, validation, replay, and as-of queries;
- automated acceptance evidence.

### 5.2 Explicitly forbidden now

- strategy optimization or claims of alpha;
- Qlib model training;
- NautilusTrader or LEAN bake-off;
- reinforcement learning;
- LLM or multi-agent orchestration;
- vector search as a source of truth;
- Neo4j or another specialized graph database;
- broker or exchange order submission;
- IBKR, OANDA, Kraken, MT5, Tradovate, Alpaca, or Coinbase adapters;
- portfolio, margin, or position sizing;
- probability calibration and expected-value trading;
- dashboards, TradingView integration, mobile apps, notifications, or visual polish;
- production Kubernetes, multi-region deployment, or premature distributed systems;
- scraping a consumer charting site as a market-data source; and
- purchasing the complete provider stack.

Interfaces may reserve clean extension points for later phases. Do not implement later-phase behavior behind those interfaces.

---

## 6. Provisional implementation baseline

Use this baseline unless an ADR documents a measured incompatibility:

- **Language:** Python 3.12
- **Packaging and lock:** `pyproject.toml` plus a committed deterministic lockfile
- **Domain validation:** Pydantic v2 models with strict mode where practical
- **Relational persistence:** PostgreSQL
- **Migrations:** Alembic
- **Object storage:** S3-compatible storage; MinIO is acceptable locally
- **Event transport:** a typed event-log interface with deterministic in-memory/fixture implementation; a Redpanda-compatible adapter may be added inside Phase 1 only if the vertical slice needs it
- **Testing:** pytest, Hypothesis where state or timestamp combinations benefit from property testing
- **Static quality:** Ruff and strict type checking
- **Containers:** Docker Compose for repeatable local dependencies
- **Observability:** structured JSON logging, correlation IDs, and OpenTelemetry-compatible boundaries

Do not let the framework define the domain. Canonical models live in a dependency-light domain package.

---

## 7. Required repository shape

Use this as the default. An ADR may refine names, but not collapse boundaries.

```text
market-intelligence-os/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── uv.lock or equivalent deterministic lock
├── compose.yaml
├── .env.example
├── .gitignore
├── Makefile
├── docs/
│   ├── architecture/
│   │   ├── constitution.md
│   │   ├── clock-semantics.md
│   │   ├── data-lineage.md
│   │   └── phase-boundaries.md
│   ├── adr/
│   │   ├── README.md
│   │   ├── template.md
│   │   └── 0001-foundation-stack.md
│   └── runbooks/
│       ├── local-development.md
│       ├── capture-and-replay.md
│       └── incident-quarantine.md
├── src/market_intelligence_os/
│   ├── domain/
│   │   ├── clocks.py
│   │   ├── identifiers.py
│   │   ├── instruments.py
│   │   ├── licenses.py
│   │   ├── provenance.py
│   │   ├── raw.py
│   │   ├── market_events.py
│   │   ├── information_events.py
│   │   └── snapshots.py
│   ├── ports/
│   │   ├── market_data_source.py
│   │   ├── raw_store.py
│   │   ├── event_store.py
│   │   ├── event_log.py
│   │   └── clock.py
│   ├── adapters/
│   │   ├── fixtures/
│   │   ├── postgres/
│   │   ├── s3/
│   │   └── providers/
│   ├── ingestion/
│   │   ├── gateway.py
│   │   ├── normalization.py
│   │   ├── deduplication.py
│   │   ├── sequence.py
│   │   └── quarantine.py
│   ├── timemachine/
│   │   ├── policies.py
│   │   ├── query.py
│   │   ├── replay.py
│   │   └── manifests.py
│   └── cli/
├── migrations/
├── fixtures/
│   ├── market/
│   ├── macro/
│   ├── news/
│   └── invalid/
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   ├── property/
│   └── acceptance/
├── scripts/
└── artifacts/
    └── acceptance/
```

Generated acceptance artifacts may be retained selectively. Never commit licensed raw payloads unless their terms explicitly permit it.

---

## 8. Canonical contracts

Use stable opaque identifiers. Use decimals for prices and quantities; do not use binary floating point for financial values. Use timezone-aware UTC instants and preserve source representations separately.

### 8.1 ClockSet

```text
ClockSet
  event_time: datetime | null
  exchange_time: datetime | null
  provider_time: datetime | null
  published_at: datetime | null
  provider_first_seen_at: datetime | null
  provider_updated_at: datetime | null
  ingested_at: datetime
  system_time: datetime
  source_timestamp_text: string | null
  source_timezone: string | null
  source_precision: enum
```

Rules:

- `ingested_at` is assigned at the ingestion boundary by an injected clock.
- `system_time` is assigned when the durable record is committed.
- tests must inject deterministic clocks;
- no parser may substitute one semantic clock for a missing different clock;
- clock inversions are quarantined or explicitly policy-classified; and
- leap seconds, daylight-saving ambiguity, and subsecond precision are handled deliberately.

### 8.2 PointInTimeQuality

```text
LIVE_CAPTURED
PROVIDER_FIRST_SEEN_VERIFIED
PUBLISHER_TIMESTAMP_ONLY
RECONSTRUCTED
UNKNOWN
```

Latency-sensitive research may later use only the first two unless an experiment explicitly declares otherwise.

### 8.3 LicensePolicy

```text
LicensePolicy
  license_policy_id
  provider_id
  permitted_environments[]
  permitted_uses[]
  redistribution: enum
  display_rights: enum
  model_training_rights: enum
  retention_policy
  derived_data_policy
  effective_from
  effective_to
  terms_reference
  reviewed_at
```

The policy engine must be capable of denying storage, display, export, or model use. A missing policy defaults to deny outside isolated tests.

### 8.4 RawEnvelope

```text
RawEnvelope
  raw_envelope_id
  source_id
  adapter_version
  retrieval_method
  clocks: ClockSet
  content_type
  content_encoding
  payload_length
  payload_sha256
  object_uri
  source_sequence
  license_policy_id
  capture_session_id
  correlation_id
```

The object identified by `object_uri` must reproduce the exact original bytes whose digest equals `payload_sha256`.

### 8.5 CanonicalMarketEvent

```text
CanonicalMarketEvent
  event_id
  source_id
  source_event_id | null
  source_sequence | null
  instrument_id
  event_type
  schema_version
  clocks: ClockSet
  bid | null
  ask | null
  price | null
  quantity | null
  side | null
  book_level | null
  revision_id | null
  supersedes_event_id | null
  raw_envelope_id
  payload_sha256
  adapter_version
  license_policy_id
  point_in_time_quality
```

Support only event types needed by the chosen vertical slice. Do not pretend to support L2/L3 if the sample contains only trades, quotes, or bars.

### 8.6 CanonicalInformationEvent

```text
CanonicalInformationEvent
  event_id
  canonical_event_id
  source_id
  source_event_id
  source_type
  source_tier
  clocks: ClockSet
  update_version
  supersedes_event_id | null
  is_correction
  is_retraction
  headline | null
  body_reference | null
  entities[]
  instruments[]
  event_categories[]
  publisher | null
  wire_service | null
  upstream_provider | null
  provenance_root_id
  raw_envelope_id
  payload_sha256
  license_policy_id
  adapter_version
  schema_version
  point_in_time_quality
```

Revisions are new records. The latest representation is a query result, never an overwritten fact.

### 8.7 SnapshotManifest

```text
SnapshotManifest
  snapshot_id
  created_at
  cutoff
  visibility_policy
  replay_snapshot_system_time
  source_ids[]
  schema_versions{}
  adapter_versions{}
  license_policy_versions{}
  raw_payload_hashes[]
  canonical_event_hash
  configuration_hash
  code_commit
  random_seed | null
```

A replay result is invalid if its manifest cannot be reconstructed.

---

## 9. Persistence rules

### 9.1 Immutable raw lake

- Content-address objects by SHA-256.
- Write original bytes before normalization.
- Treat an existing digest as idempotent success, not a second object.
- Store capture metadata separately from object bytes so the same payload can be observed more than once.
- Verify digest after write and during replay sampling.
- Quarantine digest mismatches.
- Do not rewrite raw objects during schema migrations.

### 9.2 Canonical event store

- Canonical fact tables are append-only.
- Use `supersedes_event_id`, `update_version`, and query-time ranking rather than replacing earlier facts.
- Enforce stable uniqueness rules without erasing repeated observations that have distinct provenance or arrival times.
- Persist the adapter and schema versions used for every transformation.
- Preserve normalization failures and rejected records in a quarantine ledger.
- Make migrations forward and backward testable against representative fixtures.

### 9.3 Provenance

At minimum, preserve this directed chain:

```text
source -> raw envelope -> canonical event -> snapshot -> replay result
```

Information events also preserve publisher, wire, aggregator, provider, and internal transformation relationships so duplicate reporting cannot later masquerade as independent evidence.

---

## 10. Time Machine semantics

Implement two explicit policies. Never expose a generic `latest_before()` helper that obscures which clock governs visibility.

### 10.1 Public-information replay

Purpose: reconstruct what the outside world could have known according to defensible publication or dissemination evidence.

For an information-event version to be visible:

```text
published_at <= cutoff
AND system_time <= replay_snapshot_system_time
AND license policy permits the query
AND the version is the latest visible version of its canonical event at cutoff
```

If `published_at` is missing or its quality is insufficient, the event is unavailable unless the query explicitly permits a lower quality class and records that downgrade in the manifest.

### 10.2 System-realistic replay

Purpose: reconstruct what this specific system had actually received.

For a record to be visible:

```text
ingested_at <= cutoff
AND system_time <= replay_snapshot_system_time
AND license policy permits the query
AND the version is the latest version actually received by cutoff
```

An item published at `09:30:00.000` but ingested at `09:30:00.842` is unavailable to a system-realistic replay during the first 842 milliseconds.

### 10.3 Revision visibility

At cutoff `T`, select only versions whose governing knowledge timestamp is `<= T`, then resolve the latest visible version by `update_version`, governing timestamp, provider sequence, and deterministic tie-breaker.

Never let a later correction, retraction, macro vintage, filing, or cleaned value leak into an earlier cutoff.

### 10.4 Deterministic ordering

Define and test a total order. The default is:

```text
governing visibility time
-> source sequence when trustworthy
-> event time
-> source ID
-> source event ID
-> raw payload hash
```

If the provider's documented semantics require another order, record it in the adapter contract and an ADR.

---

## 11. Phase 0 — Constitution and contracts

### Goal

Create a repository that makes incorrect time, provenance, license, and phase behavior difficult to express.

### Required work

1. Establish the repository structure, development commands, dependency lock, and local services.
2. Write `AGENTS.md` containing the authority hierarchy, no-live rule, phase boundary, required validation commands, and prohibition on fake completion.
3. Write the project constitution and ADR template.
4. Implement the canonical contracts in Section 8.
5. Implement injected clock interfaces and reject naive datetimes.
6. Implement canonical serialization with stable field order and hashing.
7. Implement license-policy evaluation with deny-by-default behavior.
8. Define schema-version compatibility rules.
9. Create deterministic fixtures for valid and invalid clocks, precision, instruments, payloads, and licenses.
10. Configure lint, type checks, unit tests, property tests, migration checks, secret scanning, and CI.
11. Add a runtime guard that proves broker SDKs and order-submission modules are absent.
12. Create acceptance-manifest generation.

### Mandatory Phase 0 tests

- naive datetime rejected;
- UTC conversion preserves original timestamp text and source timezone;
- source precision is preserved without invented digits;
- decimal financial values serialize deterministically;
- identical contract serializations produce identical hashes;
- missing license policy denies non-test use;
- prohibited redistribution path is rejected;
- schema version mismatch fails explicitly;
- a deterministic injected clock makes repeated tests byte-identical;
- importing the project exposes no live order function; and
- a clean checkout can run the full Phase 0 verification command.

### Phase 0 gate

Store:

```text
artifacts/acceptance/phase-0/manifest.json
artifacts/acceptance/phase-0/test-results.xml
artifacts/acceptance/phase-0/schema-contracts.json
artifacts/acceptance/phase-0/environment.json
artifacts/acceptance/phase-0/hashes.json
```

The gate passes only if a clean environment reproduces the same schema and fixture hashes. If it fails, stop and fix Phase 0 before Phase 1.

---

## 12. Phase 1 — One market-data vertical slice

### Goal

Prove one lawful source and one instrument can travel from original bytes through normalization into deterministic replay without losing time, sequence, provenance, rights, or payload identity.

### Provider and instrument rule

- Start with a `FixtureMarketDataSource` containing redistributable synthetic or explicitly permitted samples.
- The first real provider candidate is the easiest lawfully accessible source consistent with the Architecture Lock; Massive is the provisional broad-market default, but economics, sample access, and terms must be verified before integration.
- Use only one liquid instrument: EUR/USD or a liquid futures contract such as CME Micro E-mini S&P 500.
- Record the choice, entitlement, event types, timestamp semantics, precision, rate limits, and redistribution constraints in an ADR.
- If no approved sample or credential exists, complete the fixture path, create the provider adapter contract and entitlement checklist, then report the real-capture gate as blocked. Never scrape or substitute an unapproved source.

### Required work

1. Implement the provider-neutral `MarketDataSource` port.
2. Implement the deterministic fixture adapter first.
3. Implement the selected real adapter only after entitlement is documented.
4. Capture raw bytes and receipt metadata before parsing.
5. Verify the object digest after persistence.
6. Normalize only the event types genuinely supplied.
7. Validate instrument identity and session/calendar metadata.
8. Deduplicate idempotent retries without deleting distinct observations.
9. Detect sequence gaps, regressions, duplicates, and clock anomalies.
10. Quarantine invalid payloads with reason codes and raw references.
11. Persist canonical events append-only.
12. Implement replay from captured event log with injected clock.
13. Provide CLI commands similar to:

```text
mios capture --source <source> --instrument <instrument> --duration <duration>
mios validate-capture --session <capture_session_id>
mios replay --session <capture_session_id> --manifest <output>
mios inspect-raw --sha256 <digest>
mios inspect-quarantine --session <capture_session_id>
```

The exact command syntax may differ, but the capabilities and machine-readable outputs are required.

### Mandatory Phase 1 fixtures

- valid ordered trade or quote stream;
- exact duplicate delivery;
- same economic event delivered twice with different receipt times;
- out-of-order event time with valid source sequence;
- source-sequence gap;
- source-sequence regression;
- malformed payload;
- unknown instrument;
- timestamp with lower precision than internal storage;
- raw object digest mismatch; and
- payload blocked by license policy.

### Mandatory Phase 1 tests

- raw payload round-trips byte-for-byte;
- normalization links every event to its raw envelope and adapter version;
- retrying ingestion is idempotent;
- distinct arrivals are not falsely collapsed;
- sequence incidents are detected and stored;
- invalid events never enter canonical fact tables;
- quarantine remains auditable;
- replay ordering is stable across processes;
- identical captured input produces identical canonical hashes; and
- a disallowed license blocks downstream routing.

### Phase 1 gate

The fixture gate requires a complete deterministic round trip. The real-capture gate additionally requires one lawfully captured session and one permitted historical sample.

Store:

```text
artifacts/acceptance/phase-1/manifest.json
artifacts/acceptance/phase-1/capture-summary.json
artifacts/acceptance/phase-1/raw-hashes.json
artifacts/acceptance/phase-1/canonical-hash.json
artifacts/acceptance/phase-1/sequence-incidents.json
artifacts/acceptance/phase-1/quarantine-summary.json
artifacts/acceptance/phase-1/replay-comparison.json
artifacts/acceptance/phase-1/license-evaluation.json
```

Do not describe Phase 1 as fully complete if only the fixture gate passed. Use `FIXTURE_VERIFIED_REAL_CAPTURE_PENDING`.

After the fixture gate passes, Phase 2 engineering may proceed against sealed fixtures while real-provider access is pending. The overall foundation must continue to report the missing real-capture gate and may not be described as production-ready.

---

## 13. Phase 2 — Point-in-time Time Machine

### Goal

Prove the system can answer, reproducibly: **What exactly was visible under a declared knowledge policy at historical cutoff T?**

### Required work

1. Implement the two visibility policies in Section 10 as separate typed strategies.
2. Implement append-only event versions and deterministic latest-visible resolution.
3. Implement snapshot manifests with code, configuration, schema, adapter, license, and payload hashes.
4. Add an ALFRED-style macro vintage fixture with at least three revisions.
5. Add a news lifecycle fixture containing CREATE, UPDATE, CORRECTION, and RETRACTION versions.
6. Add late-arrival and backfilled-archive fixtures.
7. Implement point-in-time quality filtering.
8. Implement as-of queries for market and information events.
9. Implement deterministic replay from a snapshot manifest.
10. Ensure a snapshot cannot query records whose `system_time` is later than the replay snapshot.
11. Produce a visibility explanation for every included or excluded event.
12. Provide CLI commands similar to:

```text
mios snapshot create --cutoff <timestamp> --policy <public|system-realistic>
mios asof query --snapshot <snapshot_id> --instrument <instrument>
mios asof explain --snapshot <snapshot_id> --event <event_id>
mios replay snapshot --snapshot <snapshot_id>
mios compare-snapshots --left <id> --right <id>
```

### Required adversarial fixtures

#### TM-001 — Future leakage sentinel

Create an event with:

- an early `event_time`;
- a correction published and ingested after the historical cutoff; and
- a later `system_time`.

Every query before the permitted knowledge timestamp must return zero visibility for the correction.

#### TM-002 — Revision replay

Create an original macro value, first revision, and second revision. Query before and after each publication/receipt boundary. Each cutoff must return exactly the version visible under the selected policy.

#### TM-003 — Late arrival

Create an article published at `09:30:00.000` and ingested at `09:30:00.842`.

- public-information replay may expose it at publication if the quality policy permits;
- system-realistic replay must hide it for the first 842 milliseconds.

#### TM-004 — Archive backfill guard

Load a historical archive today whose old items contain publisher timestamps but no verified historical receipt times. Public replay may use them only at their declared quality. System-realistic replay must not pretend they were received historically.

#### TM-005 — Retraction and correction

An original item is updated, corrected, then retracted. Earlier cutoffs see earlier versions. Later cutoffs see the retraction state. No historical query is retroactively cleaned.

#### TM-006 — COT-style two-clock case

Create a positioning record describing Tuesday but published Friday. A Wednesday cutoff must not see it.

#### TM-007 — Snapshot isolation

Create snapshot S1, ingest additional backfilled records, then rerun S1. Its results and hashes must remain identical. A new snapshot S2 may see the additional records according to policy.

### Mandatory Phase 2 tests

- all TM fixtures pass under both visibility policies;
- point-in-time quality filters are enforced and recorded;
- later corrections never leak backward;
- macro revisions resolve correctly;
- retractions do not erase history;
- archive publication time is never copied into historical receipt time;
- snapshot replay is stable after later ingestion;
- visibility explanations include the governing clock and policy;
- identical snapshots produce identical result hashes; and
- a clean environment reproduces the complete Phase 2 artifact set.

### Phase 2 gate

Store:

```text
artifacts/acceptance/phase-2/manifest.json
artifacts/acceptance/phase-2/tm-001.json
artifacts/acceptance/phase-2/tm-002.json
artifacts/acceptance/phase-2/tm-003.json
artifacts/acceptance/phase-2/tm-004.json
artifacts/acceptance/phase-2/tm-005.json
artifacts/acceptance/phase-2/tm-006.json
artifacts/acceptance/phase-2/tm-007.json
artifacts/acceptance/phase-2/snapshot-reproducibility.json
artifacts/acceptance/phase-2/visibility-policy-matrix.json
artifacts/acceptance/phase-2/final-hashes.json
```

The gate passes only when every adversarial fixture produces its expected visibility matrix and a clean rerun reproduces the hashes.

Then stop. Print the Phase 2 completion report and wait for explicit approval of the Phase 3 prompt.

---

## 14. Acceptance-evidence contract

Every acceptance artifact must include:

```text
acceptance_test_id
phase
status
started_at
completed_at
code_commit
working_tree_state
environment_hash
configuration_hash
schema_versions
adapter_versions
fixture_ids
input_hashes
expected_result
actual_result
output_hashes
commands_executed
failure_reason | null
```

Rules:

- Never edit a failed artifact into a passing artifact.
- A rerun creates a new attempt linked to the earlier attempt.
- Store machine-readable outputs first; human summaries are secondary.
- A coverage percentage is not a substitute for an acceptance case.
- If a provider entitlement blocks a test, mark `BLOCKED`, name the missing authority, and preserve all independently completed evidence.

---

## 15. Required engineering behavior

For every phase:

1. Inspect the repository and current branch before editing.
2. State the phase goal, files expected to change, and tests that define completion.
3. Make small, reviewable commits with precise messages.
4. Keep provider SDKs behind adapters.
5. Use deterministic clocks and fixtures in tests.
6. Run formatting, linting, type checks, unit tests, integration tests, migration tests, secret scanning, and the phase acceptance suite.
7. Render a concise evidence summary from stored artifacts.
8. Stop on failed gates; do not rationalize them.
9. Preserve unrelated user changes.
10. Never claim that a skeleton, placeholder, mocked response, dashboard, or README proves completion.

Do not leave `TODO`, `pass`, fake data, or unimplemented branches on a path required by a phase gate. Test fixtures must be explicitly labeled and impossible to confuse with real market data.

---

## 16. Completion reports

At the end of each phase, return:

```text
PHASE
STATUS: PASSED | FAILED | BLOCKED | FIXTURE_VERIFIED_REAL_CAPTURE_PENDING

DELIVERED
- ...

ACCEPTANCE TESTS
- ID: result, evidence path

COMMANDS RUN
- ...

HASHES
- ...

KNOWN LIMITATIONS
- ...

BLOCKERS REQUIRING ALEX
- exact action required, if any

NEXT PERMITTED STEP
- one step only
```

The report must distinguish verified behavior from planned behavior.

---

## 17. Final instruction

Build the truth machine first.

Do not optimize a strategy. Do not connect a broker. Do not add an LLM. Do not create a dashboard. Do not claim profit. Do not hide uncertainty about when information was knowable.

Success for Phases 0–2 means this statement is demonstrably true:

> Given a historical cutoff, a declared visibility policy, a sealed snapshot, and an event ID, the system can prove why each version was visible or invisible, trace every visible fact to immutable original bytes, reproduce the ordered replay and hashes, and prevent anything learned later from leaking backward.

When that statement passes all required acceptance tests, stop and wait for the next authorized phase.
