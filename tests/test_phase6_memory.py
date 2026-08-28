"""Phase 6: MEM-001..MEM-004 + LLM authority boundary."""
from __future__ import annotations

import unittest

from mios.memory.semantic_memory import (
    LLMAuthorityError, Proposal, SemanticMemory, UnvalidatedMemoryError,
)


def prop(pid, roots=("a" * 64,), **kw):
    return Proposal(proposal_id=pid, author_kind=kw.pop("author", "llm"), text="fixture conclusion",
                    evidence_roots=roots, **kw)


class MEM001_UnvalidatedBlocked(unittest.TestCase):
    def test_unvalidated_llm_text_rejected(self):
        m = SemanticMemory()
        with self.assertRaises(UnvalidatedMemoryError):
            m.admit(prop("p1"), validated=False, validator_id="det-val-1",
                    valid_from="2026-01-05T00:00:00+00:00", memory_id="m1")

    def test_validated_admitted(self):
        m = SemanticMemory()
        rec = m.admit(prop("p2"), validated=True, validator_id="det-val-1",
                      valid_from="2026-01-05T00:00:00+00:00", memory_id="m2")
        self.assertEqual(rec.validated_by, "det-val-1")


class MEM002_TemporalValidity(unittest.TestCase):
    def test_future_memory_invisible_early(self):
        m = SemanticMemory()
        m.admit(prop("p3"), True, "det-val-1", "2026-03-01T00:00:00+00:00", "m3")
        self.assertEqual(m.visible_at("2026-02-01T00:00:00+00:00"), [])
        self.assertEqual(len(m.visible_at("2026-03-02T00:00:00+00:00")), 1)


class MEM003_IndependenceNotInflated(unittest.TestCase):
    def test_four_conclusions_one_root(self):
        m = SemanticMemory()
        shared = ("b" * 64,)
        recs = [m.admit(prop(f"p{i}", roots=shared), True, "det-val-1",
                        "2026-01-05T00:00:00+00:00", f"m{i}") for i in range(4)]
        self.assertEqual(m.independence(recs), 1)


class MEM004_GraveyardQueryable(unittest.TestCase):
    def test_failures_remain(self):
        m = SemanticMemory()
        m.bury("failed_hypothesis", {"experiment_id": "exp-neg", "reason": "no net edge"})
        m.bury("incident", {"kind_detail": "gap", "source": "FIXTURE"})
        self.assertEqual(len(m.graveyard()), 2)
        self.assertEqual(m.graveyard("failed_hypothesis")[0]["experiment_id"], "exp-neg")


class LLMBoundary(unittest.TestCase):
    def test_llm_cannot_invent_numbers(self):
        m = SemanticMemory()
        with self.assertRaises(LLMAuthorityError):
            m.admit(prop("p9", proposed_numeric_inputs=("price=104.2",)), True, "det-val-1",
                    "2026-01-05T00:00:00+00:00", "m9")

    def test_llm_cannot_approve_risk_or_size(self):
        m = SemanticMemory()
        with self.assertRaises(LLMAuthorityError):
            m.admit(prop("pa", requests_risk_approval=True), True, "v", "2026-01-05T00:00:00+00:00", "ma")
        with self.assertRaises(LLMAuthorityError):
            m.admit(prop("pb", requests_position_size=True), True, "v", "2026-01-05T00:00:00+00:00", "mb")


if __name__ == "__main__":
    unittest.main()
