"""Runtime guard: prove broker SDKs and order-submission paths are absent (Law 14)."""
from __future__ import annotations

import os
import re
from typing import Dict, List

FORBIDDEN_IMPORTS = (
    "ib_insync", "ibapi", "alpaca", "alpaca_trade_api", "ccxt", "oandapyV20",
    "robin_stocks", "kiteconnect", "tda", "binance", "coinbase", "kraken",
)

_ORDER_SYMBOL = re.compile(
    r"def\s+(submit_live_order|place_live_order|send_live_order|execute_live_order)\b"
)


def scan_tree_for_live_authority(root: str) -> Dict:
    """Static scan of the source tree for broker SDK imports and live order symbols."""
    findings: List[Dict] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "artifacts", ".venv"}]
        for fn in filenames:
            if not fn.endswith(".py") or fn == "no_live_authority.py":
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            for mod in FORBIDDEN_IMPORTS:
                if re.search(rf"^\s*(import|from)\s+{re.escape(mod)}\b", text, re.M):
                    findings.append({"file": path, "kind": "forbidden_broker_sdk", "detail": mod})
            match = _ORDER_SYMBOL.search(text)
            if match:
                findings.append({"file": path, "kind": "live_order_symbol", "detail": match.group(0)})
    return {"clean": not findings, "findings": findings}


def assert_package_exposes_no_live_order(package) -> None:
    """Importing the project must expose no live order function."""
    for name in dir(package):
        lowered = name.lower()
        if "order" in lowered and ("submit" in lowered or "place" in lowered or "send" in lowered):
            raise AssertionError(f"package exposes suspicious live-order symbol: {name}")
