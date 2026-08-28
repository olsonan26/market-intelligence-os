"""Regex + entropy secret scanner. Failures are gate failures."""
from __future__ import annotations

import math
import os
import re
from typing import Dict, List

PATTERNS = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key_block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("generic_api_key", re.compile(r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"][A-Za-z0-9+/_\-]{16,}['\"]")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[a-z0-9\._\-]{20,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
]

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {c: s.count(c) for c in set(s)}
    return -sum((n / len(s)) * math.log2(n / len(s)) for n in freq.values())

def scan(root: str) -> Dict:
    findings: List[Dict] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Scan authored and distributable files, not downloaded dependencies or
        # generated framework output. Those trees can contain documentation
        # fixtures that intentionally resemble keys.
        dirnames[:] = [
            d for d in dirnames
            if d not in {".git", "__pycache__", "artifacts", ".venv", "node_modules", ".next", ".vercel"}
        ]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            try:
                with open(path, encoding="utf-8", errors="strict") as fh:
                    text = fh.read()
            except (UnicodeDecodeError, OSError):
                continue
            for name, pat in PATTERNS:
                for m in pat.finditer(text):
                    findings.append({"file": path, "kind": name, "match": m.group(0)[:24] + "..."})
    return {"clean": not findings, "findings": findings}
