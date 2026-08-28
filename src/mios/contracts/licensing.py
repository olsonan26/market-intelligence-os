"""Machine-enforceable license policy (Laws 6/7: rights are data; deny by default)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LicenseUse(Enum):
    INTERNAL_RESEARCH = "internal_research"
    DERIVED_SIGNALS = "derived_signals"
    REDISTRIBUTION = "redistribution"
    PUBLIC_DISPLAY = "public_display"
    TEST_FIXTURE = "test_fixture"


class LicenseViolation(PermissionError):
    """A use is not permitted by the governing license policy."""


@dataclass(frozen=True)
class LicensePolicy:
    license_id: str
    internal_research: bool = False
    derived_signals: bool = False
    redistribution: bool = False
    public_display: bool = False

    def permits(self, use: LicenseUse) -> bool:
        if use is LicenseUse.TEST_FIXTURE:
            return True
        return {
            LicenseUse.INTERNAL_RESEARCH: self.internal_research,
            LicenseUse.DERIVED_SIGNALS: self.derived_signals,
            LicenseUse.REDISTRIBUTION: self.redistribution,
            LicenseUse.PUBLIC_DISPLAY: self.public_display,
        }[use]

    def to_canonical_dict(self) -> dict:
        return {
            "schema": "mios.license_policy",
            "license_id": self.license_id,
            "internal_research": self.internal_research,
            "derived_signals": self.derived_signals,
            "redistribution": self.redistribution,
            "public_display": self.public_display,
        }


def enforce_license(policy: Optional[LicensePolicy], use: LicenseUse) -> None:
    """Missing policy denies every non-test use."""
    if policy is None:
        if use is LicenseUse.TEST_FIXTURE:
            return
        raise LicenseViolation(f"no license policy attached: use '{use.value}' denied by default")
    if not policy.permits(use):
        raise LicenseViolation(f"license '{policy.license_id}' does not permit use '{use.value}'")
