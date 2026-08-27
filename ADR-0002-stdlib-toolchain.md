# ADR-0002: Stdlib toolchain for checks in this build environment

**Status:** Accepted
**Decision changed:** Spec requires ruff/black/mypy/pytest/property tests/CI runners.
**Forcing evidence:** No package installation path exists in the build sandbox (pip cannot reach the network);
pytest, mypy, ruff, black, hypothesis are not importable. Recorded in the preflight manifest.
**Decision:** Implement checks with the standard library: `unittest` for unit/contract/integration/adversarial
tests, `compileall`+`ast` based lint gate (syntax, forbidden imports, no TODO/pass on gated paths), a custom
deterministic property-harness (seeded exhaustive/randomized cases), and a regex+entropy secret scanner.
CI config (`.github/workflows/ci.yml`) is committed so that a normal environment runs the full commercial
toolchain; `tools/run_checks.py` detects available tools and uses the strictest available.
**Affected invariants:** none - determinism, evidence, and gate discipline are preserved.
**Regression tests:** the check runner itself is exercised by the phase gates.
**Rollback path:** environments with the full toolchain automatically use it via tools/run_checks.py.
