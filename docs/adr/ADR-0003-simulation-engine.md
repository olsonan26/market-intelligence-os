# ADR-0003: Simulation engine selection state

**Status:** Accepted (bake-off EXTERNAL_VERIFICATION_PENDING)
**Context:** Phase 3 requires a measured NautilusTrader-vs-LEAN bake-off. Neither engine is installable
in this build environment (no network package installation; no .NET runtime for LEAN). Fabricating
bake-off numbers is prohibited.
**Decision:** Implement the framework-neutral `SimulationEngine` contract now, with a fully deterministic
reference engine (`DeterministicSimEngine`) that enforces the contract: ordered canonical-event consumption,
friction model (commission, spread, slippage, funding, margin), latency and partial-fill modeling,
checkpoint/restart, and hash-stable outputs. NautilusTrader and LEAN adapter stubs implement ONLY the port
signature and raise `EntitlementPending` on construction — they cannot silently run.
**State:** SIM-001..SIM-007 are verified against the contract via the reference engine (fixture verification).
SIM-008 (weighted scorecard selection) is BLOCKED: it requires installing both engines and running the
benchmark suite. The scorecard template and benchmark fixtures are committed and ready to run.
**What Alex must provide:** an environment with `pip install nautilus_trader` and LEAN CLI (dotnet) available.
**Rollback:** none needed; the reference engine remains the deterministic cross-check either way.
