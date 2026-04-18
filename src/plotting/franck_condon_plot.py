"""Franck-Condon diagram plotter — fixed-template schematic (v7).

Draws a spectroscopy-oriented Franck-Condon diagram. The curve shapes,
transitions, and guide lines are all fixed; only numeric energy values,
compound name, and unit strings depend on the input data.

v7 change (vs v6):
- Axis label fonts ("Energy", "Reaction coordinate") now read from
  style["fc_axes"]["ylabel_fontsize"] and ["xlabel_fontsize"] instead
  of being hardcoded. This lets users tune axis label sizes from the
  style panel, which matters when exporting to single-column
  publication figures where default sizes may be too small.

v6 change: Recalibrated S1/T1 positions so the vertical absorption
arrow tip meets the S1 curve at r=0 (Franck-Condon principle).

v5 changes: L-shape axes with arrow heads; Energy label repositioned.
v4 change: Swapped S1/T1 for readability.
v3 changes: BDE removed; ISC added; blue dashed adiabatic; shallower S0.

Architecture:
- Fixed schematic with data-driven labels.
- All coordinates in normalized (0, 1) space; no numeric Y-axis ticks.
- BDE entries parsed but silently ignored.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch

from src.data.models import CompoundFranckCondon
from src.plotting.plot_helpers import convert_energy, validate_style_fonts

logger = logging.getLogger(__name__)


# =====================================================================
# Fixed template geometry (v4)
# =====================================================================

# S1 positioned so vertical absorption arrow tip (y=Y_S1_VERT_HEIGHT)
# touches the left arm of the S1 Morse curve at r=0. The math:
#   y_S1(r=0) = Y_MIN[S1] + D_DEPTH[S1] * (1 - exp(A_WIDTH[S1]*r_eq))²
# With current constants, r_eq=0.22 makes y_S1(0) ≈ 0.85, matching
# Y_S1_VERT_HEIGHT = 0.84. This satisfies the Franck-Condon principle:
# vertical excitation lands on the excited-state potential curve.
_R_EQ = {"S0": 0.00, "S1": 0.22, "T1": 0.47}

# Vertical minimum heights — S1 still above T1 in energy (unchanged)
_Y_MIN = {"S0": 0.00, "T1": 0.40, "S1": 0.60}

_D_DEPTH = {"S0": 0.40, "T1": 0.50, "S1": 0.52}
_A_WIDTH = {"S0": 2.4, "T1": 2.3, "S1": 2.4}

_R_PLOT_MIN = -0.40
_R_PLOT_MAX = 1.20
_N_POINTS = 600

_Y_TOP_CLIP = 1.05
_Y_BOTTOM = -0.08
_Y_TOP = 1.15
_X_LEFT = -0.55
_X_RIGHT = 1.50

_VIB_LEVELS_FRAC = [0.10, 0.22, 0.36, 0.52, 0.70, 0.88]

# Vertical absorption arrow reaches this y-level (represents E_S1_vertical)
_Y_S1_VERT_HEIGHT = _Y_MIN["S1"] + 0.24

# Integrated L-shape axes (v5): X and Y axes meet at a corner
_AXIS_ORIGIN_X = _X_LEFT + 0.05
_AXIS_ORIGIN_Y = _Y_BOTTOM + 0.02


# =====================================================================
# Main plotter class
# =====================================================================


class FranckCondonPlotter:
    """Renders Franck-Condon schematic diagrams with swapped S1/T1 layout."""

    def plot(
        self,
        ax: Axes,
        compound_fc_rows: list[CompoundFranckCondon],
        style: dict,
        unit: str = "kcal/mol",
        compound_name: str = "",
    ) -> dict:
        """Draw the Franck-Condon diagram on *ax*.

        Args:
            ax: Matplotlib Axes to draw into.
            compound_fc_rows: All FC sheet rows for one compound.
            style: Style dict (passed through validate_style_fonts first).
            unit: "kcal/mol" or "eV" — used for label formatting.
            compound_name: Displayed in the title as a suffix.

        Returns:
            Dict of drawn artists, keyed by semantic role.
        """
        style = validate_style_fonts(style)
        artists: dict = {}
        artists_by_id: dict = {}

        data = self._collect_data(compound_fc_rows, unit)

        ax.clear()
        ax.set_xlim(_X_LEFT, _X_RIGHT)
        ax.set_ylim(_Y_BOTTOM, _Y_TOP)
        ax.set_xticks([])
        ax.set_yticks([])
        # Hide ALL matplotlib spines — we draw custom L-shape axes in
        # _draw_energy_axis_indicator() with arrow heads on both ends.
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)

        self._draw_title(ax, style, compound_name)

        artists["curves"] = self._draw_curves(ax, style, data)
        artists["vib_levels"] = self._draw_vib_levels(ax, style, data)
        artists["wavefunctions"] = self._draw_wavefunctions(ax, style, data)
        artists["transitions"] = self._draw_transitions(ax, style, data)
        artists["isc"] = self._draw_isc(ax, style, data, artists_by_id)
        artists["guides"] = self._draw_guides(ax, style, data)
        artists["state_labels"] = self._draw_state_labels(ax, style, data, artists_by_id)
        artists["energy_labels"] = self._draw_energy_labels(
            ax, style, data, unit, artists_by_id
        )
        self._draw_energy_axis_indicator(ax, style)

        # Apply any user-dragged label position overrides
        for label_id, pos in style.get("label_overrides", {}).items():
            if label_id in artists_by_id:
                artists_by_id[label_id].set_position(tuple(pos))

        artists["by_id"] = artists_by_id
        return artists

    # ------------------------------------------------------------------
    # Data extraction
    # ------------------------------------------------------------------

    def _collect_data(
        self, rows: list[CompoundFranckCondon], unit: str
    ) -> dict:
        """Extract per-state energies. BDE entries are intentionally ignored."""

        def conv(value: Optional[float]) -> Optional[float]:
            if value is None:
                return None
            return convert_energy(value, "kcal/mol", unit)

        states: dict[str, dict] = {}
        for row in rows:
            state = row.state.upper() if row.state else ""
            if state in ("S0", "S1", "T1") and state not in states:
                states[state] = {
                    "e_vert": conv(row.e_vertical),
                    "e_ad": conv(row.e_adiabatic),
                }

        return {"states": states}

    # ------------------------------------------------------------------
    # Curve generation
    # ------------------------------------------------------------------

    @staticmethod
    def _morse_like(r: np.ndarray, state: str) -> np.ndarray:
        r_eq = _R_EQ[state]
        D = _D_DEPTH[state]
        a = _A_WIDTH[state]
        return D * (1.0 - np.exp(-a * (r - r_eq))) ** 2

    def _draw_curves(self, ax: Axes, style: dict, data: dict) -> dict:
        r = np.linspace(_R_PLOT_MIN, _R_PLOT_MAX, _N_POINTS)
        out: dict = {}
        for state in ("S0", "T1", "S1"):
            if state not in data["states"]:
                continue
            key = f"fc_{state.lower()}"
            s = style.get(key, {})
            color = s.get("color", "#333333")
            lw = s.get("linewidth", 2.2)

            y = _Y_MIN[state] + self._morse_like(r, state)
            mask = y <= _Y_TOP_CLIP
            line, = ax.plot(
                r[mask], y[mask],
                color=color, linewidth=lw, solid_capstyle="round",
                zorder=3,
            )
            out[state] = line
        return out

    def _draw_vib_levels(self, ax: Axes, style: dict, data: dict) -> dict:
        out: dict = {}
        for state in ("S0", "T1", "S1"):
            if state not in data["states"]:
                continue
            key = f"fc_{state.lower()}"
            s = style.get(key, {})
            color = s.get("color", "#333333")

            y_min = _Y_MIN[state]
            D = _D_DEPTH[state]
            r_eq = _R_EQ[state]
            a = _A_WIDTH[state]
            lines = []
            for frac in _VIB_LEVELS_FRAC:
                y_level = y_min + frac * D
                if y_level > _Y_TOP_CLIP:
                    continue
                sqrt_frac = np.sqrt(frac)
                if sqrt_frac >= 1.0:
                    continue
                x_left = r_eq - np.log(1 + sqrt_frac) / a
                x_right = r_eq - np.log(1 - sqrt_frac) / a
                ln, = ax.plot(
                    [x_left, x_right], [y_level, y_level],
                    color=color, linewidth=0.7, alpha=0.55,
                    zorder=2,
                )
                lines.append(ln)
            out[state] = lines
        return out

    def _draw_wavefunctions(self, ax: Axes, style: dict, data: dict) -> dict:
        out: dict = {}
        for state in ("S0", "T1", "S1"):
            if state not in data["states"]:
                continue
            key = f"fc_{state.lower()}"
            s = style.get(key, {})
            color = s.get("color", "#333333")

            y_min = _Y_MIN[state]
            r_eq = _R_EQ[state]
            y0 = y_min + _VIB_LEVELS_FRAC[0] * _D_DEPTH[state]

            bump_width = 0.10
            bump_height = 0.022
            x_bump = np.linspace(r_eq - bump_width, r_eq + bump_width, 60)
            y_bump = y0 + bump_height * (
                np.exp(-((x_bump - r_eq) / (bump_width * 0.4)) ** 2) - 0.5
            )
            ln, = ax.plot(
                x_bump, y_bump,
                color=color, linewidth=1.0, alpha=0.85,
                zorder=2,
            )
            out[state] = ln
        return out

    # ------------------------------------------------------------------
    # Transitions
    # ------------------------------------------------------------------

    def _draw_transitions(self, ax: Axes, style: dict, data: dict) -> dict:
        out: dict = {}
        if "S0" not in data["states"] or "S1" not in data["states"]:
            return out

        v = style.get("fc_vertical_arrow", {})
        if v.get("show", True):
            ann = ax.annotate(
                "",
                xy=(_R_EQ["S0"], _Y_S1_VERT_HEIGHT),
                xytext=(_R_EQ["S0"], _Y_MIN["S0"] + 0.02),
                arrowprops=dict(
                    arrowstyle="-|>",
                    color=v.get("color", "#3A5FCD"),
                    linewidth=v.get("linewidth", 1.8),
                    mutation_scale=15,
                ),
                zorder=5,
            )
            out["vertical"] = ann

        a_ = style.get("fc_adiabatic_arrow", {})
        if a_.get("show", True):
            arrow = FancyArrowPatch(
                (_R_EQ["S0"], _Y_MIN["S0"] + 0.02),
                (_R_EQ["S1"], _Y_MIN["S1"] + 0.02),
                arrowstyle="-|>",
                color=a_.get("color", "#3A5FCD"),
                linewidth=a_.get("linewidth", 1.5),
                linestyle="dashed",
                mutation_scale=12,
                zorder=5,
            )
            ax.add_patch(arrow)
            out["adiabatic"] = arrow

        return out

    def _draw_isc(self, ax: Axes, style: dict, data: dict, artists_by_id: dict = None) -> dict:
        """Curved dashed arrow from S1 minimum (left) to T1 minimum (right)."""
        out: dict = {}
        if "S1" not in data["states"] or "T1" not in data["states"]:
            return out

        isc = style.get("fc_isc", {})
        if not isc.get("show", True):
            return out

        color = isc.get("color", "#666666")
        linewidth = isc.get("linewidth", 1.3)

        # S1 is now at r=0.30, T1 at r=0.55; arrow goes right-down
        arrow = FancyArrowPatch(
            (_R_EQ["S1"] + 0.04, _Y_MIN["S1"] + 0.02),
            (_R_EQ["T1"] - 0.04, _Y_MIN["T1"] + 0.02),
            arrowstyle="-|>",
            color=color,
            linewidth=linewidth,
            linestyle=(0, (3, 2)),
            connectionstyle="arc3,rad=-0.3",  # curves up-right
            mutation_scale=10,
            zorder=5,
        )
        ax.add_patch(arrow)
        out["arrow"] = arrow

        if isc.get("show_label", True):
            mid_x = (_R_EQ["S1"] + _R_EQ["T1"]) / 2
            mid_y = (_Y_MIN["S1"] + _Y_MIN["T1"]) / 2 + 0.08
            label_text = isc.get("label_text", "ISC")
            fontsize = isc.get("label_fontsize", 9)
            t = ax.text(
                mid_x, mid_y, label_text,
                color=color, fontsize=fontsize, fontstyle="italic",
                ha="center", va="center",
                bbox=dict(facecolor="white", edgecolor="none",
                          alpha=0.85, pad=1),
                zorder=6,
            )
            out["label"] = t
            if artists_by_id is not None:
                artists_by_id["fc_isc_label"] = t

        return out

    # ------------------------------------------------------------------
    # Guide lines
    # ------------------------------------------------------------------

    def _draw_guides(self, ax: Axes, style: dict, data: dict) -> dict:
        g = style.get("fc_guide_lines", {})
        if not g.get("show", True):
            return {}
        color = g.get("color", "#888888")
        lw = g.get("linewidth", 0.5)
        alpha = g.get("alpha", 0.6)
        ls = g.get("linestyle", "dotted")

        out: dict = {}
        y_values = []
        if "S1" in data["states"]:
            y_values.append(("s1_vert", _Y_S1_VERT_HEIGHT))
            y_values.append(("s1_ad", _Y_MIN["S1"] + 0.02))
        if "T1" in data["states"]:
            y_values.append(("t1_ad", _Y_MIN["T1"] + 0.02))

        # Guide lines start just right of the Y-axis (not on it) and end
        # before the right edge — they visually belong inside the plot area
        x_start = _AXIS_ORIGIN_X + 0.01
        x_end = _X_RIGHT - 0.03
        for key, y in y_values:
            line, = ax.plot(
                [x_start, x_end], [y, y],
                color=color, linewidth=lw, alpha=alpha, linestyle=ls,
                zorder=1,
            )
            out[key] = line
        return out

    # ------------------------------------------------------------------
    # Text labels
    # ------------------------------------------------------------------

    def _draw_state_labels(
        self, ax: Axes, style: dict, data: dict, artists_by_id: dict = None
    ) -> dict:
        out: dict = {}
        label_x = _R_PLOT_MAX + 0.03
        for state in ("S0", "T1", "S1"):
            if state not in data["states"]:
                continue
            key = f"fc_{state.lower()}"
            s = style.get(key, {})
            color = s.get("color", "#333333")
            fontsize = s.get("label_fontsize", 13)
            text = s.get("label_text", self._default_state_label(state))
            y = _Y_MIN[state] + _D_DEPTH[state] * 0.75
            if y > _Y_TOP_CLIP:
                y = _Y_TOP_CLIP - 0.02
            t = ax.text(
                label_x, y, text,
                color=color, fontsize=fontsize, fontweight="bold",
                ha="left", va="center",
                zorder=4,
            )
            out[state] = t
            if artists_by_id is not None:
                artists_by_id[f"fc_{state.lower()}_label"] = t
        return out

    @staticmethod
    def _default_state_label(state: str) -> str:
        return {
            "S0": "$\\mathbf{S_0}$",
            "S1": "$\\mathbf{S_1}$",
            "T1": "$\\mathbf{T_1}$",
        }[state]

    def _draw_energy_labels(
        self, ax: Axes, style: dict, data: dict, unit: str,
        artists_by_id: dict = None,
    ) -> dict:
        out: dict = {}
        decimals = 2 if unit == "eV" else 1

        def fmt(v: float) -> str:
            return f"{v:.{decimals}f}"

        states = data["states"]
        bbox = dict(facecolor="white", edgecolor="none",
                    alpha=0.85, pad=1.5)

        if "S1" in states and states["S1"]["e_vert"] is not None:
            s = style.get("fc_s1", {})
            color = s.get("color", "#3A5FCD")
            fs = s.get("value_fontsize", 9)
            t = ax.text(
                _R_EQ["S0"] - 0.05, _Y_S1_VERT_HEIGHT,
                f"$S_1^{{ver}}$={fmt(states['S1']['e_vert'])} {unit}",
                color=color, fontsize=fs,
                ha="right", va="center",
                zorder=6, bbox=bbox,
            )
            out["s1_vert"] = t
            if artists_by_id is not None:
                artists_by_id["fc_s1_vert"] = t

        # S1 ad: place to the right of S1 minimum.
        if "S1" in states and states["S1"]["e_ad"] is not None:
            s = style.get("fc_s1", {})
            color = s.get("color", "#3A5FCD")
            fs = s.get("value_fontsize", 9)
            t = ax.text(
                _R_EQ["S1"] + 0.12, _Y_MIN["S1"] + 0.02,
                f"$S_1^{{ad}}$={fmt(states['S1']['e_ad'])} {unit}",
                color=color, fontsize=fs,
                ha="left", va="center",
                zorder=6, bbox=bbox,
            )
            out["s1_ad"] = t
            if artists_by_id is not None:
                artists_by_id["fc_s1_ad"] = t

        # T1 ad: T1 now at r=0.55 with room on its right.
        if "T1" in states and states["T1"]["e_ad"] is not None:
            s = style.get("fc_t1", {})
            color = s.get("color", "#2E8B57")
            fs = s.get("value_fontsize", 9)
            t = ax.text(
                _R_EQ["T1"] + 0.12, _Y_MIN["T1"] + 0.02,
                f"$T_1^{{ad}}$={fmt(states['T1']['e_ad'])} {unit}",
                color=color, fontsize=fs,
                ha="left", va="center",
                zorder=6, bbox=bbox,
            )
            out["t1_ad"] = t
            if artists_by_id is not None:
                artists_by_id["fc_t1_ad"] = t

        return out

    # ------------------------------------------------------------------
    # Axis decoration
    # ------------------------------------------------------------------

    def _draw_energy_axis_indicator(self, ax: Axes, style: dict) -> None:
        """Draw integrated L-shape axes (X + Y meeting at a corner).

        This replaces the previous disconnected axis lines. Both axes
        terminate in arrow heads, in the textbook style.

        Reads font sizes from style['fc_axes'] so users can tune labels
        from the style panel. Defaults chosen for good readability in
        single-column publications.
        """
        fc_axes = style.get("fc_axes", {})
        axis_color = fc_axes.get("color", "#333333")
        axis_lw = fc_axes.get("linewidth", 1.3)
        ylabel_fs = fc_axes.get("ylabel_fontsize", 11)
        xlabel_fs = fc_axes.get("xlabel_fontsize", 10)
        ylabel_text = fc_axes.get("ylabel_text", "Energy")
        xlabel_text = fc_axes.get("xlabel_text", "Reaction coordinate (r)")

        # Y-axis — from origin corner up to top, with arrow head
        ax.annotate(
            "",
            xy=(_AXIS_ORIGIN_X, _Y_TOP - 0.01),
            xytext=(_AXIS_ORIGIN_X, _AXIS_ORIGIN_Y),
            arrowprops=dict(arrowstyle="-|>", color=axis_color,
                            linewidth=axis_lw, mutation_scale=14),
            zorder=2,
        )

        # X-axis — from origin corner to right edge, with arrow head
        ax.annotate(
            "",
            xy=(_X_RIGHT - 0.02, _AXIS_ORIGIN_Y),
            xytext=(_AXIS_ORIGIN_X, _AXIS_ORIGIN_Y),
            arrowprops=dict(arrowstyle="-|>", color=axis_color,
                            linewidth=axis_lw, mutation_scale=14),
            zorder=2,
        )

        # "Energy" label — placed to the LEFT of the Y-axis to avoid
        # overlap with in-plot energy annotations like $S_1^{ver}=73.3$
        ax.text(
            _AXIS_ORIGIN_X - 0.04, (_AXIS_ORIGIN_Y + _Y_TOP) / 2,
            ylabel_text,
            color=axis_color, fontsize=ylabel_fs, fontweight="bold",
            rotation=90, ha="center", va="center",
            zorder=2,
        )

        # "Reaction coordinate (r)" label below X-axis
        ax.text(
            (_AXIS_ORIGIN_X + _X_RIGHT) / 2, _AXIS_ORIGIN_Y - 0.04,
            xlabel_text,
            color=axis_color, fontsize=xlabel_fs, fontstyle="italic",
            ha="center", va="top",
            zorder=2,
        )

    def _draw_title(
        self, ax: Axes, style: dict, compound_name: str
    ) -> None:
        base = style.get("title", {}).get("text", "Franck-Condon Diagram")
        fontsize = style.get("title", {}).get("fontsize", 13)
        if base.strip().lower() == "molecular energy diagram":
            base = "Franck-Condon Diagram"
        title = f"{base}: {compound_name}" if compound_name else base
        ax.set_title(title, fontsize=fontsize, fontweight="bold", pad=10)