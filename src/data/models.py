"""Data model dataclasses for DFT calculation results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CompoundHomoLumo:
    """HOMO and LUMO orbital energies for a single compound.

    Args:
        name: Compound identifier string.
        homo: HOMO energy in eV (typically negative).
        lumo: LUMO energy in eV (typically negative).
    """

    name: str
    homo: float
    lumo: float

    @property
    def gap(self) -> float:
        """HOMO-LUMO gap in eV (LUMO - HOMO)."""
        return self.lumo - self.homo


@dataclass
class CompoundStates:
    """Electronic state energies for a single compound.

    Args:
        name: Compound identifier string.
        s0: Ground state energy in eV (typically 0.0).
        s1: First singlet excited state energy in eV.
        t1: First triplet state energy in eV.
    """

    name: str
    s0: float
    s1: float
    t1: float


@dataclass
class CompoundFranckCondon:
    """Franck-Condon potential energy surface data for one compound/state entry.

    Args:
        name: Compound identifier string.
        state: Electronic state label — "S0", "S1", or "T1".
        e_vertical: Vertical excitation energy (kcal/mol or eV).
        e_adiabatic: Adiabatic excitation energy (kcal/mol or eV).
        bde_value: Optional bond dissociation energy value.
        bde_label: Optional BDE annotation label string.
    """

    name: str
    state: str
    e_vertical: float
    e_adiabatic: float
    bde_value: Optional[float] = None
    bde_label: Optional[str] = None


@dataclass
class DFTDataset:
    """Container for all three DFT data tables.

    Args:
        homo_lumo: List of HOMO/LUMO entries.
        states: List of electronic state entries.
        franck_condon: List of Franck-Condon entries.
    """

    homo_lumo: list[CompoundHomoLumo]
    states: list[CompoundStates]
    franck_condon: list[CompoundFranckCondon]

    @classmethod
    def empty(cls) -> DFTDataset:
        """Return a dataset with all three lists empty."""
        return cls([], [], [])
