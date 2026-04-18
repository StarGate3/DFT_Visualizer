"""Validation logic for DFT datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.data.models import DFTDataset


@dataclass
class ValidationWarning:
    """A single validation issue found in a DFTDataset.

    Args:
        severity: ``"warning"`` for soft issues, ``"error"`` for hard violations.
        message: Human-readable description of the issue.
        compound_name: Name of the offending compound, or None if not applicable.
        sheet: Name of the sheet the issue originates from.
    """

    severity: str
    message: str
    compound_name: Optional[str]
    sheet: str


def validate_dataset(dataset: DFTDataset) -> list[ValidationWarning]:
    """Validate all entries in a DFTDataset and return any issues found.

    Checks performed:
    - HOMO/LUMO sheet: gap must be positive (error), HOMO/LUMO should be
      negative, HOMO outlier detection (< -15 eV), duplicate names.
    - States sheet: ordering S0 ≤ T1 ≤ S1 (warning), S1-T1 gap in typical
      range [0.1, 1.5] eV (warning), duplicate names.
    - FranckCondon sheet: duplicate (name, state) pairs.

    Args:
        dataset: The dataset to validate.

    Returns:
        A list of :class:`ValidationWarning` objects. Empty list if all good.
    """
    issues: list[ValidationWarning] = []

    # ------------------------------------------------------------------
    # HOMO/LUMO
    # ------------------------------------------------------------------
    seen_hl: set[str] = set()
    for c in dataset.homo_lumo:
        if c.name in seen_hl:
            issues.append(ValidationWarning(
                severity="warning",
                message=f"Duplicate compound name '{c.name}'",
                compound_name=c.name,
                sheet="HOMO_LUMO",
            ))
        seen_hl.add(c.name)

        if c.homo >= c.lumo:
            issues.append(ValidationWarning(
                severity="error",
                message=(
                    f"HOMO ({c.homo:.3f} eV) \u2265 LUMO ({c.lumo:.3f} eV); "
                    "gap must be positive"
                ),
                compound_name=c.name,
                sheet="HOMO_LUMO",
            ))

        if c.homo > 0:
            issues.append(ValidationWarning(
                severity="warning",
                message=f"HOMO value ({c.homo:.3f} eV) is positive — typically negative",
                compound_name=c.name,
                sheet="HOMO_LUMO",
            ))

        if c.lumo > 0:
            issues.append(ValidationWarning(
                severity="warning",
                message=f"LUMO value ({c.lumo:.3f} eV) is positive — typically negative",
                compound_name=c.name,
                sheet="HOMO_LUMO",
            ))

        if c.homo < -15:
            issues.append(ValidationWarning(
                severity="warning",
                message=f"HOMO value ({c.homo:.3f} eV) is suspiciously low (< -15 eV)",
                compound_name=c.name,
                sheet="HOMO_LUMO",
            ))

    # ------------------------------------------------------------------
    # States
    # ------------------------------------------------------------------
    seen_st: set[str] = set()
    for c in dataset.states:
        if c.name in seen_st:
            issues.append(ValidationWarning(
                severity="warning",
                message=f"Duplicate compound name '{c.name}'",
                compound_name=c.name,
                sheet="States",
            ))
        seen_st.add(c.name)

        if not (c.s0 <= c.t1 <= c.s1):
            issues.append(ValidationWarning(
                severity="warning",
                message=(
                    f"Expected S0 \u2264 T1 \u2264 S1, "
                    f"got S0={c.s0:.3f}, T1={c.t1:.3f}, S1={c.s1:.3f} eV"
                ),
                compound_name=c.name,
                sheet="States",
            ))

        st_gap = c.s1 - c.t1
        if not (0.1 <= st_gap <= 1.5):
            issues.append(ValidationWarning(
                severity="warning",
                message=(
                    f"S1\u2013T1 gap ({st_gap:.3f} eV) is outside the typical "
                    "range [0.1, 1.5] eV"
                ),
                compound_name=c.name,
                sheet="States",
            ))

    # ------------------------------------------------------------------
    # FranckCondon
    # ------------------------------------------------------------------
    seen_fc: set[str] = set()
    for entry in dataset.franck_condon:
        key = f"{entry.name}|{entry.state}"
        if key in seen_fc:
            issues.append(ValidationWarning(
                severity="warning",
                message=(
                    f"Duplicate entry for compound '{entry.name}', "
                    f"state '{entry.state}'"
                ),
                compound_name=entry.name,
                sheet="FranckCondon",
            ))
        seen_fc.add(key)

    return issues
