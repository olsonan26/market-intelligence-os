"""Validated Semantic Memory with temporal validity and independence discipline (Phase 6).

MEM-001: unvalidated LLM text cannot enter validated memory.
MEM-002: temporal validity prevents future versions appearing early.
MEM-003: N agent conclusions sharing one evidence root do not inflate independence.
MEM-004: failed hypotheses and incidents remain queryable forever.

LLM boundary (constitutional law 8): LLM output is a PROPOSAL. It may not carry numeric
market inputs of its own invention, approve risk, size positions, or bypass validation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple


class UnvalidatedMemoryError(PermissionError):
    """An unvalidated proposal attempted to enter Validated Semantic Memory."""


class LLMAuthorityError(PermissionError):
    """An LLM proposal attempted a prohibited authority (numbers, risk, sizing, execution)."""


@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    author_kind: str                  # "llm" | "human" | "statistical"
    text: str
    evidence_roots: Tuple[str, ...]
    proposed_numeric_inputs: Tuple[str, ...] = tuple()   # LLMs may NOT invent these
    requests_risk_approval: bool = False
    requests_position_size: bool = False


@dataclass(frozen=True)
class ValidatedMemoryRecord:
    memory_id: str
    proposal_id: str
    content: str
    evidence_roots: Tuple[str, ...]
    validated_by: str                 # deterministic validator id, never an LLM
    valid_from: str
    superseded_from: Optional[str] = None


class SemanticMemory:
    def __init__(self) -> None:
        self._validated: List[ValidatedMemoryRecord] = []
        self._graveyard: List[dict] = []   # failed hypotheses & incidents, queryable forever

    def guard_llm_authority(self, p: Proposal) -> None:
        if p.author_kind == "llm":
            if p.proposed_numeric_inputs:
                raise LLMAuthorityError("LLMs cannot invent numeric inputs")
            if p.requests_risk_approval:
                raise LLMAuthorityError("LLMs cannot approve risk")
            if p.requests_position_size:
                raise LLMAuthorityError("LLMs cannot size positions")

    def admit(self, p: Proposal, validated: bool, validator_id: str, valid_from: str,
              memory_id: str) -> ValidatedMemoryRecord:
        self.guard_llm_authority(p)
        if not validated:
            raise UnvalidatedMemoryError("only validated conclusions enter Validated Semantic Memory")
        if not p.evidence_roots:
            raise UnvalidatedMemoryError("validated memory requires evidence roots")
        rec = ValidatedMemoryRecord(memory_id, p.proposal_id, p.text, p.evidence_roots,
                                    validator_id, valid_from)
        self._validated.append(rec)
        return rec

    def bury(self, kind: str, detail: dict) -> None:
        self._graveyard.append({"kind": kind, **detail})

    def graveyard(self, kind: Optional[str] = None) -> List[dict]:
        return [g for g in self._graveyard if kind is None or g["kind"] == kind]

    def visible_at(self, cutoff: str) -> List[ValidatedMemoryRecord]:
        return [r for r in self._validated if r.valid_from <= cutoff]

    def independence(self, records: Sequence[ValidatedMemoryRecord]) -> int:
        roots: Set[str] = set()
        for r in records:
            roots.update(r.evidence_roots)
        return len(roots)
