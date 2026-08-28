# FOX TRADING

FOX TRADING is a point-in-time-correct, multi-market intelligence and experimentation OS with an evidence-first operator console. Built per `docs/specifications/PHASE_0_2_MASTER_BUILD_PROMPT.md` and `docs/specifications/PHASE_0_11_FULL_BUILD_MASTER_PLAN.md`.

**No live-trading capability exists in this repository, and none can be enabled by configuration.**

## Operator console

The Next.js console is designed to make each decision understandable before it becomes actionable:

- Guided mode teaches first-time users how to read the screen.
- Every probability, expected-value figure, and freshness signal explains what it means.
- Evidence lineage opens from the decision instead of living in a separate audit tool.
- Fixture mode is visually persistent, and the UI cannot place real orders.
- Eight working views cover markets, point-in-time replay, research, decisions, risk, memory, and system health.

```bash
npm ci
npm run dev
```

## Verification

```bash
npm run verify
for phase in 0 1 2 3 4 5 6 7 8 9 10 11; do python tools/run_checks.py --phase "$phase"; done
python tools/phase2_evidence.py
python tools/e2e_sealed_scenario.py
```

- Constitution: `AGENTS.md`
- ADRs: `docs/adr/`
- Build state: `docs/build/BUILD_STATE.json`
- Design system: `docs/design/UI_DESIGN_SYSTEM.md`
- Acceptance evidence: `artifacts/acceptance/`

A README claim proves nothing; run the gates.
