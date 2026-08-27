# Market Intelligence OS — Constitution (AGENTS.md)

**Authority:** Architecture Lock V1 -> PHASE_0_11_FULL_BUILD_MASTER_PLAN.md -> PHASE_0_2_MASTER_BUILD_PROMPT.md -> ADRs -> tickets.

## Non-negotiable laws (enforced in code and tests, not slogans)

1. Point-in-time truth: replay sees only records permitted by the selected visibility policy at or before its cutoff.
2. Four clocks: `event_time`, `published_at`, `ingested_at`, `system_time` are semantically distinct and preserved.
3. Knowledge time is never fabricated: `published_at` is never copied into `ingested_at` unless capture was genuine.
4. Raw payloads, event versions, corrections, retractions, incidents, and provenance edges are append-only.
5. Raw before normalized: original bytes are stored and hashed before canonical transformation.
6. Provenance before confidence: derived records point to independent evidence roots.
7. Rights are data: every payload and derived record carries a machine-enforceable license policy; missing policy denies non-test use.
8. Provider neutrality: domain code consumes canonical contracts, never provider payload models.
9. UTC internally: naive timestamps are rejected; source timezone and raw timestamp text are preserved.
10. Precision is never invented.
11. Deterministic replay: identical log + code + config + snapshot + seed => identical ordered outputs and hashes.
12. Failures become evidence (incidents), never silent drops.
13. No fake completion: a phase is incomplete until every required acceptance case produces stored evidence.
14. No live authority: no broker SDK imports, no order routes, no live-trading credentials. Maximum authority is
    verified paper/sandbox operation and zero-order-authority shadow operation. No configuration flag may bypass this.

## Repository visibility boundary

This repository is intentionally PUBLIC by explicit human authorization, valid ONLY while it contains:
no secrets, no credentials, no licensed raw payloads without redistribution rights, no private brokerage
information, no proprietary datasets, no personal information, and no live-trading functionality.
The preflight gate re-verifies this boundary and records it in `artifacts/acceptance/preflight/manifest.json`.

## ADR process

Material deviations require an ADR in `docs/adr/` stating: decision changed, forcing evidence, affected
invariants/schemas, migration consequences, regression tests, rollback path. Never silently reinterpret a requirement.

## Verification

The Phase 0 verification command is:

    python tools/run_checks.py --phase 0

It runs the mandatory contract tests, the secret scan, the no-live-authority guard, and writes the
machine-readable acceptance artifacts under `artifacts/acceptance/`.
