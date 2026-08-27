# MARKET INTELLIGENCE OS
## Full Build Master Plan — Phases 0–11

**Version:** 1.0

**Repository:** `olsonan26/market-intelligence-os`

**Status:** Authorized full-platform construction plan

**Build boundary:** Backtest, research, simulation, paper execution, and shadow operation are authorized. Live-capital execution is not authorized.

---

## 1. Purpose and authority

This document expands Market Intelligence OS construction from the foundation-only scope into the complete Phase 0–11 platform.

The existing file:

`docs/specifications/PHASE_0_2_MASTER_BUILD_PROMPT.md`

remains the authoritative detailed specification for Phases 0, 1, and 2. Its instruction to stop after Phase 2 is superseded only by this document: after the complete Phase 2 gate passes, continue sequentially through Phases 3–11 under the gates below.

All other Phase 0–2 contracts, fixtures, invariants, evidence requirements, and prohibitions remain in force.

When requirements conflict, use this hierarchy:

1. law, licensing, security, and explicit human authorization;
2. Architecture Lock V1 invariants;
3. this Full Build Master Plan;
4. the Phase 0–2 Master Build Prompt;
5. accepted Architecture Decision Records;
6. implementation tickets, code comments, and framework defaults.

Any material deviation requires an ADR with evidence, affected invariants, migration impact, regression tests, and rollback path.

---

## 2. Final product definition

Build a point-in-time-correct, multi-market, event-driven Market Intelligence and Experimentation Operating System that can:

- ingest licensed market, macro, filing, positioning, news, and account-state events;
- preserve immutable original evidence and every known version;
- reconstruct what was publicly knowable and what this specific system had received at any historical cutoff;
- create versioned feature and evidence sets without future leakage;
- run statistical, machine-learning, reinforcement-learning, and bounded language-model hypotheses inside a governed model arena;
- compare hypotheses against no-trade and simpler baselines;
- validate with purged chronological methods, realistic frictions, robustness tests, and deterministic replay;
- convert validated forecasts into empirically calibrated probabilities and net expected value;
- enforce deterministic portfolio, exposure, margin, freshness, and kill-switch policies;
- translate approved venue-neutral TradeIntents into capability-checked paper orders;
- reconstruct orders, partial fills, positions, and account state through an append-only ledger and reconciliation;
- operate in real-time shadow mode with zero order authority;
- expose every number and decision through an auditable operator dashboard; and
- survive restarts, outages, corrupt payloads, late arrivals, provider changes, and failed experiments without inventing truth.

This is not a profit promise. Its first job is to distinguish reproducible evidence from attractive nonsense.

---

## 3. Permanent constitutional laws

These rules apply to every phase:

1. Point-in-time truth governs all research and replay.
2. `event_time`, `published_at`, `ingested_at`, and `system_time` remain semantically distinct.
3. Knowledge timestamps are never fabricated.
4. Raw and canonical evidence is append-only.
5. Provenance roots are counted once, regardless of how many agents repeat them.
6. License rights are machine-enforced data.
7. Provider and broker payloads never become domain contracts.
8. LLMs cannot invent numeric inputs, approve risk, size positions, or bypass validation.
9. Risk decisions are deterministic and reproducible.
10. No-trade is a first-class action.
11. All results are evaluated net of spread, fees, slippage, funding or swap, latency, partial fills, margin, and market impact assumptions.
12. Research, replay, shadow, paper, and eventual live paths share canonical events and order semantics.
13. Broker streams, snapshots, and the internal ledger reconcile continuously.
14. Displayed probabilities are empirical, not raw model confidence.
15. Champion/challenger promotion requires pre-registered gates.
16. Failures, rejected hypotheses, incidents, drift, and regime breakdowns become queryable memory.
17. Humans control authority. Nothing in this plan authorizes live capital.
18. A phase is incomplete until its required acceptance evidence is stored and reproducible.

---

## 4. Repository and execution protocol

### 4.1 Long-running branch

Use a long-running branch:

`codex/full-build`

Open one draft pull request into `main` titled:

`Full Build: Market Intelligence OS Phases 0–11`

Commit each phase separately. Never squash phase boundaries while the build is in progress.

Recommended commit prefixes:

```text
phase0:
phase1:
phase2:
phase3:
phase4:
phase5:
phase6:
phase7:
phase8:
phase9:
phase10:
phase11:
```

### 4.2 Resumable build state

Maintain:

`docs/build/BUILD_STATE.json`

Required shape:

```text
build_id
master_plan_version
branch
head_commit
current_phase
current_ticket
phase_statuses{}
last_passing_gate
acceptance_artifact_paths[]
external_verifications_pending[]
blocked_items[]
adrs[]
known_limitations[]
next_permitted_action
updated_at
```

Update it after every meaningful commit, test run, failure, and phase gate. A new coding session must read this file and acceptance artifacts before editing.

### 4.3 Progression rule

After a phase gate passes:

1. generate and verify its acceptance artifacts;
2. update `BUILD_STATE.json`;
3. commit the completed phase;
4. update the draft pull request summary; and
5. continue automatically to the next phase.

Do not ask Alex for routine framework or implementation choices already resolved by this plan. Stop only when:

- an acceptance gate fails and cannot be safely repaired;
- credentials, licensing, funding, legal approval, or another human authority is required;
- two architecture options remain materially different after a required bake-off;
- a destructive operation requires approval;
- continuing would violate a constitutional law; or
- live-capital authority would be required.

### 4.4 Public repository boundary

The repository is intentionally public for now. This is authorized only under these conditions:

- no credentials or secrets;
- no licensed raw payloads without explicit redistribution rights;
- no private account identifiers or brokerage data;
- no proprietary datasets or paid research documents;
- no personal information; and
- no live-trading functionality.

Enforce secret scanning and payload-license checks. Public visibility does not relax any rights policy.

---

## 5. Cross-phase definition of done

Every phase must include:

- working code on required paths;
- schema and migration updates;
- unit, contract, integration, property, and acceptance tests where applicable;
- deterministic fixtures;
- structured logs, metrics, traces, and correlation IDs;
- threat and failure cases relevant to the phase;
- runbook updates;
- machine-readable acceptance evidence;
- reproducibility hashes;
- clean-checkout verification;
- updated architecture and API documentation;
- updated `BUILD_STATE.json`; and
- a completion report distinguishing verified, fixture-only, sandbox-verified, blocked, and planned behavior.

Forbidden completion shortcuts:

- placeholder implementations;
- hard-coded success responses;
- mocked acceptance results;
- screenshots as proof;
- README claims without stored evidence;
- test-count or coverage-only claims;
- silently skipped tests;
- swallowed exceptions;
- fake provider, broker, or model outputs presented as real; and
- moving failed requirements into “future work” without explicit authorization.

---

## 6. Phases 0–2 — Foundation and Time Machine

Implement Phases 0–2 exactly as specified in:

`docs/specifications/PHASE_0_2_MASTER_BUILD_PROMPT.md`

Required result before Phase 3:

> Given a historical cutoff, visibility policy, sealed snapshot, and event ID, the system can prove why each version was visible or invisible, trace visible facts to immutable original bytes, reproduce ordered replay and hashes, and prevent later knowledge from leaking backward.

The Phase 2 gate must pass all required Time Machine fixtures. If real-provider access is pending, fixture-mode construction may continue only with the incomplete external verification plainly recorded.

---

## 7. Phase 3 — Deterministic research world

### Goal

Select and integrate the primary event-driven simulation engine through a measured NautilusTrader-versus-LEAN bake-off using identical canonical events and assumptions.

### Required work

1. Build a framework-neutral `SimulationEngine` contract.
2. Create adapters for NautilusTrader and QuantConnect LEAN sufficient to run the identical benchmark suite.
3. Feed both engines the same sealed Time Machine snapshot and total-ordered event log.
4. Use the same instrument definitions, sessions, exchange calendars, price precision, quantity precision, corporate actions, futures rolls, FX conversion, and margin assumptions.
5. Model market, limit, stop, and stop-limit orders where both engines support them.
6. Model configurable latency, spread, commission, slippage, funding or swap, partial fills, rejects, and cancellations.
7. Inject macro and news events as custom canonical data.
8. Test restart and deterministic state restoration.
9. Measure runtime, memory, adapter complexity, custom-data quality, research-to-paper parity, and reproducibility.
10. Write an ADR selecting the primary engine. Retain the loser only as a useful cross-check or interoperability reference.

### Acceptance tests

- `SIM-001`: identical ordered inputs are consumed by both adapters.
- `SIM-002`: repeated runs within each engine produce identical orders, fills, P&L, and hashes.
- `SIM-003`: latency and partial-fill fixtures produce the declared results.
- `SIM-004`: commission, spread, slippage, funding or swap, and margin change results predictably.
- `SIM-005`: FX account conversion and futures roll fixtures reconcile.
- `SIM-006`: custom macro/news events arrive only at permitted knowledge times.
- `SIM-007`: restart from checkpoint reproduces uninterrupted execution.
- `SIM-008`: the selected engine wins a documented weighted scorecard, not preference.

### Gate

Select one primary deterministic market world and store the bake-off evidence, benchmark data, scorecard, ADR, and reproducibility hashes. Do not operate two production simulation truths.

---

## 8. Phase 4 — Research and validation engine

### Goal

Create a sealed model arena where hypotheses compete against no-trade and simpler baselines under leakage-safe, cost-aware, reproducible validation.

### Required work

1. Implement versioned `FeatureDefinition`, `FeatureSet`, `DatasetSnapshot`, `Hypothesis`, `ExperimentManifest`, `ModelArtifact`, and `PromotionDecision` contracts.
2. Build a point-in-time feature registry with lineage to canonical events and code versions.
3. Implement chronological train, validation, and untouched test windows.
4. Implement purging and embargo for overlapping labels.
5. Add walk-forward evaluation, multiple seeds, adjacent periods, parameter perturbation, regime splits, and vendor-discrepancy tests.
6. Implement a baseline ladder: no-trade/cash, naive market, simple rules, linear/logistic, classical time series, gradient boosting, deep learning, RL, and bounded LLM-assisted hypotheses.
7. Integrate Microsoft Qlib as the provisional experiment/research adapter without granting it execution authority.
8. Implement experiment pre-registration and immutable result artifacts.
9. Implement a champion/challenger registry with locked promotion thresholds.
10. Store negative and rejected results permanently.

### Acceptance tests

- `VAL-001`: a deliberately future-leaking feature is rejected.
- `VAL-002`: purged/embargoed splits remove overlapping-label contamination.
- `VAL-003`: a zero-cost winner that loses after realistic costs is rejected.
- `VAL-004`: repeated hypothesis testing is recorded and adjusted or explicitly bounded.
- `VAL-005`: a clean environment reproduces predictions, trades, metrics, and hashes.
- `VAL-006`: a fragile model fails perturbation or adjacent-period robustness.
- `VAL-007`: a challenger failing any pre-registered threshold remains `NOT_ELIGIBLE` despite higher headline return.
- `VAL-008`: every feature value traces to permitted point-in-time inputs.
- `VAL-009`: no-trade defeats strategies with insufficient net edge.

### Gate

Demonstrate one simple valid baseline and one intentionally invalid model. The system must accept and reject them for the correct, stored reasons.

---

## 9. Phase 5 — News, macro, filings, positioning, and provenance

### Goal

Turn external information into versioned canonical evidence with defensible arrival clocks and independent provenance roots.

### Required work

1. Extend `CanonicalInformationEvent` and provenance contracts without breaking Time Machine semantics.
2. Integrate official sources first: SEC EDGAR, Federal Reserve, ECB, ALFRED, and CFTC COT where lawful and technically available.
3. Add provisional Benzinga and Trading Economics adapters behind entitlement gates.
4. Add GDELT for broad geopolitical context, never as the low-latency canonical wire.
5. Add Event Registry only if commercial terms and value justify it.
6. Preserve CREATE, UPDATE, CORRECTION, REMOVE, and RETRACTION lifecycles.
7. Preserve publisher, wire, aggregator, analytics provider, and internal transformation provenance.
8. Entity-link sources to canonical instruments with versioned mappings and confidence.
9. Deduplicate article propagation while preserving every source observation.
10. Create source-reputation inputs: latency, correction rate, coverage, provenance quality, and historical predictive usefulness.

### Acceptance tests

- `NEWS-001`: a correction is invisible before its permitted clock.
- `NEWS-002`: a retraction does not erase earlier historical views.
- `NEWS-003`: five downstream reports from one press release count as one independent root.
- `NEWS-004`: SEC acceptance/dissemination time governs filing visibility.
- `NEWS-005`: ALFRED revisions resolve to correct historical vintages.
- `NEWS-006`: Tuesday COT observations remain invisible before Friday publication.
- `NEWS-007`: provider publication time is never fabricated as historical receipt time.
- `NEWS-008`: entity mappings are versioned and auditable.
- `NEWS-009`: license policy blocks prohibited article body storage or display.

### Gate

At several historical cutoffs, the Time Machine must return exactly the permitted article versions, macro vintages, filings, and positioning records with complete provenance explanations.

---

## 10. Phase 6 — Memory, graph intelligence, and bounded orchestration

### Goal

Create typed, temporally valid memory and evidence graphs that support reasoning without allowing agents or vectors to become truth.

### Required memory classes

- Immutable Market Memory
- Trade Episodic Memory
- Validated Semantic Memory
- Procedural Memory
- Regime Memory
- Source Reputation
- Agent Reputation
- Failure Memory
- Calibration Memory

### Required work

1. Implement typed memory records with event time, known-at time, validity, provenance, owner, review state, and schema version.
2. Use PostgreSQL edge tables as the V1 evidence graph.
3. Use PostgreSQL plus pgvector provisionally for similarity indexing; vectors are never canonical truth.
4. Implement graph paths from source to event to feature to hypothesis to forecast to risk decision to order/fill/outcome.
5. Implement evidence-root independence and duplicate-source collapse.
6. Implement semantic-memory write gates requiring validated evidence and review state.
7. Implement failure-memory capture from rejected models, data incidents, operational failures, and false positives.
8. Implement a typed graph runner for bounded reasoning subgraphs.
9. Implement a provider-neutral model gateway recording model, prompt version, input hashes, output, latency, token usage, cost, privacy class, and policy decision.
10. Allow LLMs to summarize evidence and propose hypotheses. Prohibit them from inventing market values, approving risk, or directly creating executable orders.
11. Evaluate Temporal for durable workflow only if long-running recovery needs justify it. Evaluate Ray only for measured distributed compute pressure.

### Acceptance tests

- `MEM-001`: unvalidated LLM text cannot enter Validated Semantic Memory.
- `MEM-002`: temporal validity prevents a future memory version from appearing early.
- `MEM-003`: four agent conclusions sharing one evidence root do not inflate independence.
- `MEM-004`: failed hypotheses and incidents remain queryable after later successes.
- `MEM-005`: vector similarity cannot override canonical filtering or license policy.
- `MEM-006`: every reasoning output reconstructs its prompt, model, sources, versions, cost, and policy.
- `MEM-007`: workflow restart resumes idempotently without duplicating side effects.
- `MEM-008`: source and agent reputation use measured history, sample size, and regime context.

### Gate

Demonstrate an evidence graph containing competing conclusions, shared provenance, failures, and temporal revisions. Confidence must depend on independent roots and validated history rather than agent count.

---

## 11. Phase 7 — Probability, expected value, and deterministic risk

### Goal

Convert validated forecasts into calibrated probabilities and deterministic portfolio decisions that prefer no-trade when evidence, liquidity, calibration, or net expected value is inadequate.

### Required work

1. Implement `CalibratedForecast`, `OutcomeDefinition`, `CalibrationModel`, `ExpectedValueEstimate`, `RiskPolicy`, and `RiskDecision` contracts.
2. Implement Brier score, log loss, reliability diagrams, sample-size reporting, uncertainty intervals, and expected calibration error.
3. Implement Platt scaling, isotonic regression, and a documented calibration-selection procedure where appropriate.
4. Track calibration by model, event definition, horizon, instrument, regime, and probability bin.
5. Detect calibration drift and distribution shift.
6. Compute expected gain, expected loss, expected friction, uncertainty penalty, and net expected value.
7. Implement no-trade/abstention thresholds.
8. Implement deterministic limits for position and portfolio exposure, currency, country, sector, strategy, evidence root, correlation, concentration, margin, drawdown, order rate, stale data, market hours, and volatility states.
9. Implement global, venue, strategy, and instrument kill switches.
10. Keep risk decisions independent from LLM output.

### Acceptance tests

- `PR-001`: displayed probability bins match realized frequencies within declared tolerance on untouched data.
- `PR-002`: calibration reports sample size and uncertainty.
- `PR-003`: distribution shift triggers downgrade, abstention, or recalibration policy.
- `EV-001`: net expected value includes every configured friction.
- `EV-002`: a positive raw edge with negative net EV becomes no-trade.
- `RS-001`: stale market, news, or account state blocks new entries while risk-reducing actions remain possible.
- `RS-002`: correlated signals cannot bypass portfolio concentration limits.
- `RS-003`: margin and liquidation thresholds reject unsafe intents.
- `RS-004`: kill switches are deterministic, authenticated, logged, and testable.
- `NT-001`: inadequate evidence quality or calibration produces abstention and no TradeIntent.

### Gate

Demonstrate that a nominal 70% forecast is displayed only with appropriate historical calibration evidence and that negative net EV, stale data, or risk breaches reliably produce no-trade.

---

## 12. Phase 8 — Broker-neutral paper execution

### Goal

Translate approved venue-neutral TradeIntents into safe paper orders while preserving an append-only execution ledger and continuously reconciled account state.

### Required contracts

- `TradeIntent`
- `CancelIntent`
- `BrokerCapabilities`
- `Order`
- `ExecutionEvent`
- `Fill`
- `Position`
- `AccountState`
- `MarginState`
- `ReconciliationResult`

### Required work

1. Implement a broker-neutral execution domain independent of simulation and model frameworks.
2. Implement pre-submission capability checks.
3. Distinguish native brackets/OCO/OTO/OTOCO from cloud-emulated contingencies.
4. Reject unsafe emulation where process failure could orphan risk.
5. Persist original broker messages beside normalized append-only execution events.
6. Implement idempotent client order IDs and duplicate-submission protection.
7. Reconcile broker stream, REST snapshot, and internal ledger into canonical account state.
8. Implement restart recovery, partial fills, rejects, cancellations, replace/amend, disconnects, token refresh, rate limits, and maintenance states.
9. Integrate paper/sandbox adapters in this order where access is available: IBKR, OANDA v20, Kraken.
10. Leave Tradovate, Alpaca, MT5, and Coinbase as later adapters after the first three prove the schema.
11. No live credentials or live order routing.

### Acceptance tests

- `EX-001`: restart between partial fills reconstructs exact remaining order and position.
- `EX-002`: required native OCO unsupported by a venue is rejected, not silently emulated.
- `EX-003`: repeated submission with the same idempotency key creates no duplicate order.
- `EX-004`: disconnect plus snapshot reconciliation repairs missed stream events.
- `EX-005`: broker reject and partial-fill semantics remain venue-specific in raw data and canonical in domain state.
- `EX-006`: rate-limit and authentication failures back off without duplicate side effects.
- `EX-007`: ledger reconstruction reproduces canonical positions and cash.
- `EX-008`: capability changes invalidate unsafe pending intents.
- `EX-009`: no configuration in the repository can route a live order.

### Gate

Each integrated venue must pass the complete paper/sandbox contract suite. Missing sandbox credentials are recorded as external verification blockers; adapter code cannot be called verified from fixtures alone.

---

## 13. Phase 9 — Real-time shadow operation

### Goal

Run the entire system against live incoming information with zero order authority and measure operational truth before any paper or future live promotion.

### Required work

1. Run real-time ingestion, Time Machine snapshots, features, models, graph reasoning, calibration, risk, and would-be TradeIntents.
2. Enforce a shadow adapter that cannot submit orders.
3. Record decision latency by source, node, model, risk, and end-to-end path.
4. Compare predicted fills with paper/simulated fills without treating them as equivalent.
5. Track drift, calibration, provider gaps, stale data, cost assumptions, abstention, and incident rates.
6. Implement restart, replay catch-up, backpressure, provider reconnect, and duplicate-event recovery.
7. Create incident playbooks and an operator approval queue.
8. Define a pre-registered observation window and promotion thresholds.

### Acceptance tests

- `SH-001`: shadow mode has cryptographically/configurationally enforced zero order authority.
- `SH-002`: every decision reconstructs its complete evidence and timing lineage.
- `SH-003`: stale data halts new would-be entries.
- `SH-004`: restart catches up without duplicate decisions.
- `SH-005`: provider gap and sequence incidents trigger declared degradation behavior.
- `SH-006`: calibration or drift breach triggers abstention or downgrade.
- `SH-007`: end-to-end latency measurements use observed clocks rather than invented timestamps.
- `SH-008`: a defined observation window produces stored operational evidence.

### Gate

Shadow operation remains stable for the pre-registered window and passes tracking, freshness, drift, audit, recovery, and zero-authority thresholds.

---

## 14. Phase 10 — Operator dashboard and control plane

### Goal

Provide a thin, trustworthy operator surface where every displayed value links to canonical evidence and no frontend component computes trading truth.

### Provisional stack

- Next.js and TypeScript frontend
- FastAPI and Pydantic service boundary
- OIDC provider-neutral authentication
- OpenTelemetry-compatible observability

### Required surfaces

- system health and source freshness;
- ingestion gaps and quarantine;
- Time Machine cutoff and visibility-policy explorer;
- canonical event and revision timeline;
- provenance-root graph;
- feature and experiment lineage;
- champion/challenger registry;
- calibration and reliability views;
- net expected value breakdown;
- deterministic risk decisions and reason codes;
- shadow/paper TradeIntent, order, fill, position, account, and reconciliation timelines;
- model, agent, source, failure, regime, and calibration memory;
- acceptance evidence and build-state views;
- kill-switch and approval controls appropriate to authorized environments; and
- audit export.

### Required work

1. Implement API authorization scopes and deny-by-default roles.
2. Keep calculation and canonical truth in backend services.
3. Attach every displayed number to an evidence, snapshot, schema, and policy reference.
4. Clearly label fixture, reconstructed, delayed, shadow, paper, and unverified data.
5. Prevent TradingView or another external chart from becoming the truth source.
6. Implement accessible keyboard navigation, readable states, error recovery, responsive layout, and audit-friendly exports.
7. Never display raw model confidence as calibrated probability.

### Acceptance tests

- `UI-001`: every displayed metric deep-links to canonical lineage.
- `UI-002`: frontend modification cannot alter canonical calculations.
- `UI-003`: role restrictions block unauthorized approvals and risk controls.
- `UI-004`: fixture, shadow, paper, and real-source states cannot be visually confused.
- `UI-005`: historical cutoff never displays later versions.
- `UI-006`: stale or degraded data is obvious and blocks unsafe workflows.
- `UI-007`: core workflows pass accessibility and browser verification.
- `UI-008`: no client bundle contains secrets or provider credentials.

### Gate

An operator can reconstruct any displayed decision from source evidence through outcome, and every number is backed by a reproducible backend lineage.

---

## 15. Phase 11 — Production hardening and release candidate

### Goal

Make the complete non-live platform secure, observable, recoverable, licensed, reproducible, and operationally supportable.

### Required work

1. Complete threat modeling, security architecture, least privilege, secret management, dependency policy, SAST, supply-chain controls, and image scanning.
2. Implement backup, restore, point-in-time database recovery, raw-lake integrity verification, disaster recovery, and documented recovery objectives.
3. Run load, soak, burst, backpressure, clock-skew, network-partition, provider-outage, database-failover, object-corruption, and process-crash tests.
4. Verify audit logs, data retention, deletion boundaries, access logs, and license enforcement.
5. Complete observability dashboards, alerts, incident routing, runbooks, and postmortem templates.
6. Produce software bill of materials, migration plan, deployment manifests, environment configuration, and rollback procedures.
7. Review provider commercial terms, redistribution, storage, display, model use, and derived-data rules before enabling each external integration.
8. Verify authentication, authorization, session security, CSRF, CORS, rate limiting, validation, and injection protections.
9. Perform an end-to-end audit reconstruction from raw evidence to shadow/paper outcome.
10. Preserve the no-live boundary. Any live-capital release requires a separate written Architecture Decision and human authorization outside this plan.

### Acceptance tests

- `SEC-001`: secret scanning and runtime secret isolation pass.
- `SEC-002`: least-privilege roles prevent unauthorized data, approval, and control actions.
- `DR-001`: backup restore reproduces canonical state and acceptance hashes.
- `DR-002`: corrupted raw objects are detected and quarantined.
- `OPS-001`: load and soak targets pass with declared capacity margins.
- `OPS-002`: provider and infrastructure failure modes degrade safely.
- `OPS-003`: incident alerts and runbooks are exercised, not merely written.
- `LC-001`: prohibited licensed data cannot reach display, export, model, or public artifact paths.
- `AU-001`: a decision ID reconstructs exact sources, versions, features, models, prompts, risk policy, order transitions, reconciliation, and outcome.
- `REL-001`: a clean environment deploys the release candidate and reproduces acceptance evidence.
- `LIVE-000`: no live-capital route exists or can be enabled by configuration alone.

### Gate

Create a signed Release Candidate report for the complete non-live platform. Do not call it live-ready. State every pending commercial, sandbox, legal, operational, and human authorization explicitly.

---

## 16. End-to-end system acceptance

The final release candidate must pass a sealed scenario containing:

1. a market-data stream with duplicates, gaps, and late arrival;
2. a macro series with revisions;
3. a news event with update, correction, and retraction;
4. duplicated downstream reporting sharing one evidence root;
5. a point-in-time feature set;
6. a simple baseline and a deliberately leaky challenger;
7. calibrated probabilities with sample size and uncertainty;
8. a positive raw edge that becomes negative after friction;
9. a no-trade decision caused by stale data or poor evidence;
10. an approved paper TradeIntent;
11. a partial fill followed by restart and reconciliation;
12. a shadow decision with zero order authority; and
13. dashboard reconstruction of the full lineage.

Required outcome:

```text
immutable source bytes
-> canonical bitemporal events
-> historical as-of snapshot
-> versioned features
-> registered experiment
-> validated forecast
-> calibrated probability
-> net expected value
-> deterministic risk decision
-> no-trade or broker-neutral TradeIntent
-> paper execution events
-> reconciliation
-> outcome and memory
-> audit reconstruction
```

Every transition must have identifiers, versions, clocks, provenance, policies, and hashes.

---

## 17. External dependency and credential protocol

When a provider, broker, model, or commercial service requires human setup:

1. never invent credentials;
2. never commit secrets;
3. implement the typed port, fixture adapter, entitlement checklist, and contract tests;
4. mark the integration `FIXTURE_VERIFIED_EXTERNAL_VERIFICATION_PENDING`;
5. state the exact account, entitlement, sandbox, legal, or funding action Alex must take;
6. continue only through paths that remain scientifically valid without that external verification; and
7. never upgrade fixture verification to sandbox, paper, shadow, or production verification without observed evidence.

Provider and venue states:

```text
NOT_STARTED
CONTRACT_DEFINED
FIXTURE_VERIFIED
ENTITLEMENT_PENDING
SANDBOX_VERIFIED
PAPER_VERIFIED
SHADOW_VERIFIED
PRODUCTION_NON_LIVE_VERIFIED
BLOCKED
```

---

## 18. Phase completion report

At every phase boundary, publish:

```text
PHASE
STATUS
COMMITS
DELIVERED
SCHEMAS AND MIGRATIONS
ACCEPTANCE TESTS AND EVIDENCE PATHS
COMMANDS EXECUTED
REPRODUCIBILITY HASHES
OBSERVABILITY EVIDENCE
SECURITY AND LICENSE EVIDENCE
EXTERNAL VERIFICATIONS PENDING
KNOWN LIMITATIONS
ADRS CREATED OR CHANGED
BLOCKERS REQUIRING ALEX
NEXT PERMITTED PHASE
```

The pull request description must maintain a phase matrix showing `NOT_STARTED`, `IN_PROGRESS`, `PASSED`, `BLOCKED`, or the precise fixture/sandbox state.

---

## 19. Final completion rule

The full build is complete only when Phases 0–11 and the end-to-end sealed scenario have reproducible passing evidence, or when remaining external verifications are accurately separated from code-complete fixture paths.

The final system may backtest, research, simulate, operate in shadow mode, and use paper/sandbox execution where verified.

It may not trade live capital.

Live trading requires a separate future authorization containing capital limits, jurisdiction and broker review, operational staffing, incident ownership, explicit risk acceptance, and a new acceptance suite. No model, configuration flag, environment variable, administrator role, or coding agent may bypass that requirement.
