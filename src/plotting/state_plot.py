"""S0/S1/T1 state energy level diagram plotter."""
from __future__ import annotations
import logging
from typing import Any
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch
from src.data.models import CompoundStates
from src.plotting.plot_helpers import apply_axes_decorations, apply_x_ticks, validate_style_fonts
from src.plotting.style_presets import DEFAULT_STYLE, DiagramStyle

logger = logging.getLogger(__name__)

_HALF_WIDTH: float = 0.35    # half-width of each horizontal level line
_ABS_X_OFFSET: float = -0.45 # absorption arrow base x relative to compound centre
_ISC_X_START: float = 0.2    # ISC curve start x relative to centre (at S1)
_ISC_X_END: float = 0.4      # ISC curve end x relative to centre (at T1)

# Rough conversion: label_offset_below (pts) → data units.
# Assumes ~5.5" figure height at typical y_range. Good enough — labels can be dragged.
_PT_TO_DATA_FACTOR: float = 1.0 / (5.5 * 72)


class StateDiagramPlotter:
    """Renders S0/S1/T1 energy level diagrams onto a matplotlib Axes."""

    def __init__(self, style: DiagramStyle | None = None) -> None:
        import copy
        self._style: DiagramStyle = copy.deepcopy(style or DEFAULT_STYLE)

    def plot(
        self,
        ax: Axes,
        compounds: list[CompoundStates],
        style: DiagramStyle,
    ) -> dict[str, Any]:
        """Render state diagram onto *ax*.

        Returns:
            Dict with artist groups plus ``"by_id"`` (stable-ID text artists)
            and ``"arrow_artists"`` (arrow_type → artist for drag manager).
        """
        style = validate_style_fonts(style)
        ax.cla()
        logger.debug("StateDiagramPlotter.plot: %d compounds", len(compounds))

        if not compounds:
            ax.text(0.5, 0.5, "No state data loaded",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=14, color="#888888")
            apply_axes_decorations(ax, style)
            return {}

        artists: dict[str, list[Any]] = {
            "s0_lines": [], "s1_lines": [], "t1_lines": [],
            "abs_arrows": [], "isc_curves": [],
            "value_texts": [], "label_texts": [],
        }
        artists_by_id: dict[str, Any] = {}
        # One representative arrow per type for the drag manager
        arrow_artists: dict[str, Any] = {}

        s0_s = style.get("s0", DEFAULT_STYLE["s0"])
        s1_s = style.get("s1", DEFAULT_STYLE["s1"])
        t1_s = style.get("t1", DEFAULT_STYLE["t1"])
        abs_s = style.get("absorption_arrow", DEFAULT_STYLE["absorption_arrow"])
        isc_s = style.get("isc_curve", DEFAULT_STYLE["isc_curve"])
        lbl_s = style.get("compound_labels", DEFAULT_STYLE["compound_labels"])

        # Compute y data range for proportional offsets
        all_y = ([c.s0 for c in compounds] + [c.s1 for c in compounds]
                 + [c.t1 for c in compounds])
        y_min, y_max = min(all_y), max(all_y)
        y_range = max(y_max - y_min, 0.5)
        y_gap = max(y_range * 0.04, 0.05)

        for i, compound in enumerate(compounds):
            self._draw_levels(
                ax, i, compound, s0_s, s1_s, t1_s, lbl_s,
                artists, artists_by_id, y_gap, y_range,
            )
            self._draw_absorption(ax, i, compound, abs_s, lbl_s, artists, artists_by_id, arrow_artists)
            self._draw_isc(ax, i, compound, isc_s, lbl_s, artists, artists_by_id, arrow_artists)

        # Axes limits
        ax.set_ylim(y_min - y_range * 0.12, y_max + y_range * 0.18)

        apply_x_ticks(ax, [c.name for c in compounds], style)
        apply_axes_decorations(ax, style)

        # Apply any user-dragged label position overrides
        for label_id, pos in style.get("label_overrides", {}).items():
            if label_id in artists_by_id:
                artists_by_id[label_id].set_position(tuple(pos))

        artists["by_id"] = artists_by_id
        artists["arrow_artists"] = arrow_artists
        return artists

    # ------------------------------------------------------------------
    # Internal drawing helpers
    # ------------------------------------------------------------------

    def _draw_levels(
        self,
        ax: Axes,
        i: int,
        compound: CompoundStates,
        s0_s: dict, s1_s: dict, t1_s: dict,
        lbl_s: dict,
        artists: dict,
        artists_by_id: dict,
        y_gap: float,
        y_range: float,
    ) -> None:
        level_specs = (
            (s0_s, compound.s0, "s0_lines", "s0"),
            (t1_s, compound.t1, "t1_lines", "t1"),
            (s1_s, compound.s1, "s1_lines", "s1"),
        )
        for level_s, y, line_key, level_name in level_specs:
            (line,) = ax.plot(
                [i - _HALF_WIDTH, i + _HALF_WIDTH],
                [y, y],
                color=level_s.get("color", "#1F2E5C"),
                linewidth=level_s.get("linewidth", 1.5),
                solid_capstyle="butt",
            )
            artists[line_key].append(line)

            # Value text above the line (draggable)
            val_text = ax.text(
                i, y + y_gap,
                level_s.get("value_format", "{:.2f} eV").format(y),
                ha="center",
                va="bottom",
                fontsize=level_s.get("value_fontsize", 9),
                color=level_s.get("value_color", "#000000"),
                fontfamily=lbl_s.get("fontfamily", "DejaVu Sans"),
                clip_on=False,
            )
            artists["value_texts"].append(val_text)
            artists_by_id[f"{level_name}_value_{i}"] = val_text

            # State name label CENTERED BELOW the line (Fix 2)
            label_offset_pts = level_s.get("label_offset_below", 14)
            label_data_offset = label_offset_pts * y_range * _PT_TO_DATA_FACTOR
            name_text = ax.text(
                i,
                y - max(label_data_offset, y_gap * 0.5),
                level_s.get("label_text", ""),
                ha="center",
                va="top",
                fontsize=level_s.get("label_fontsize", 10),
                fontweight=level_s.get("label_fontweight", "bold"),
                color=level_s.get("label_color", "#000000"),
                fontfamily=lbl_s.get("fontfamily", "DejaVu Sans"),
                clip_on=False,
            )
            artists["label_texts"].append(name_text)
            artists_by_id[f"{level_name}_label_{i}"] = name_text

    def _draw_absorption(
        self,
        ax: Axes,
        i: int,
        compound: CompoundStates,
        abs_s: dict,
        lbl_s: dict,
        artists: dict,
        artists_by_id: dict,
        arrow_artists: dict,
    ) -> None:
        x_offset = abs_s.get("x_offset", 0.0)
        x_arr = i + _ABS_X_OFFSET + x_offset
        arrow = ax.annotate(
            "",
            xy=(x_arr, compound.s1),
            xytext=(x_arr, compound.s0),
            arrowprops=dict(
                arrowstyle=abs_s.get("arrow_style", "-|>"),
                color=abs_s.get("color", "#333333"),
                lw=abs_s.get("linewidth", 1.5),
                mutation_scale=14,
            ),
            annotation_clip=False,
        )
        artists["abs_arrows"].append(arrow)
        # Register representative arrow for drag manager (first compound's arrow)
        if "absorption" not in arrow_artists:
            arrow_artists["absorption"] = arrow

        if abs_s.get("show_label", True):
            mid_y = (compound.s0 + compound.s1) / 2.0
            t = ax.text(
                x_arr - 0.05,
                mid_y,
                abs_s.get("label_text", "Abs."),
                ha="right",
                va="center",
                fontsize=abs_s.get("label_fontsize", 9),
                color=abs_s.get("label_color", "#333333"),
                fontfamily=lbl_s.get("fontfamily", "DejaVu Sans"),
                clip_on=False,
            )
            artists_by_id[f"abs_label_{i}"] = t

    def _draw_isc(
        self,
        ax: Axes,
        i: int,
        compound: CompoundStates,
        isc_s: dict,
        lbl_s: dict,
        artists: dict,
        artists_by_id: dict,
        arrow_artists: dict,
    ) -> None:
        _ls_map = {"dashed": "--", "solid": "-", "dotted": ":", "dashdot": "-."}
        raw_ls = isc_s.get("linestyle", "dashed")
        mpl_ls = _ls_map.get(raw_ls, raw_ls)

        x_offset = isc_s.get("x_offset", 0.0)
        isc_start_x = i + _ISC_X_START + x_offset
        isc_end_x = i + _ISC_X_END + x_offset

        isc_patch = FancyArrowPatch(
            (isc_start_x, compound.s1),
            (isc_end_x, compound.t1),
            connectionstyle=f"arc3,rad={isc_s.get('curvature', 0.3)}",
            arrowstyle="-|>",
            color=isc_s.get("color", "#555555"),
            linewidth=isc_s.get("linewidth", 1.2),
            linestyle=mpl_ls,
            mutation_scale=12,
            zorder=3,
        )
        ax.add_patch(isc_patch)
        artists["isc_curves"].append(isc_patch)
        if "isc" not in arrow_artists:
            arrow_artists["isc"] = isc_patch

        if isc_s.get("show_label", True):
            mid_y = (compound.s1 + compound.t1) / 2.0
            t = ax.text(
                isc_end_x + 0.06,
                mid_y,
                isc_s.get("label_text", "ISC"),
                ha="left",
                va="center",
                fontsize=isc_s.get("label_fontsize", 9),
                color=isc_s.get("label_color", "#555555"),
                fontfamily=lbl_s.get("fontfamily", "DejaVu Sans"),
                clip_on=False,
            )
            artists_by_id[f"isc_label_{i}"] = t

    def update_style(self, style: DiagramStyle) -> None:
        """Store new style for reference. Full redraw is handled by the widget."""
        self._style = style
