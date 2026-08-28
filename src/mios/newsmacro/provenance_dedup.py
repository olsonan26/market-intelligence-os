"""Independence counting: N downstream reports sharing one press release = ONE root (NEWS-003).

Every source observation is preserved; only INDEPENDENCE is deduplicated (constitutional law 5).
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple


def independent_roots(observations: Iterable[dict]) -> dict:
    """observations: [{'observation_id', 'source_id', 'evidence_roots': [sha,...]}]"""
    obs = list(observations)
    roots: Set[str] = set()
    for o in obs:
        roots.update(o["evidence_roots"])
    return {
        "observation_count": len(obs),                 # every observation preserved
        "independent_root_count": len(roots),          # counted once, however many agents repeat them
        "roots": sorted(roots),
        "observations": [o["observation_id"] for o in obs],
    }
