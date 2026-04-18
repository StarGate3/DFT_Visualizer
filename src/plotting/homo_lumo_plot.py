"""HOMO/LUMO energy level diagram plotter."""

from __future__ import annotations

import copy
import logging
from typing import Any

from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from src.data.models import CompoundHomoLumo
from src.plotting.plot_helpers import apply_axes_decorations, apply_x_ticks, validate_style_fonts
from src.plotting.style_presets import DEFAULT_STYLE, DiagramStyle

logger = logging.getLogger(__name__)

# Half-width (in x-data units) of each horizontal HOMO/LUMO line segment.
_HALF_WIDTH: float = 0.30
# Horizontal offset of gap value text from arrow centre.
_GAP_TEXT_OFFSET: float = 0.12


class HomoLumoPlotter:
    """Renders a HOMO/LUMO energy level diagram onto a matplotlib Axes.

    Responsibilities:
    - Drawing HOMO and LUMO horizontal line segments.
    - Annotating energy values next to each segment.
    - Drawing a double-headed arrow for each gap with a gap-value label.
    - Applying axis labels, title, grid, and legend from the style dict.
    """

    def __init__(self, style: DiagramStyle | None = None) -> None:
        """Initialise with an optional base style (defaults to DEFAULT_STYLE)."""
        self._style: DiagramStyle = copy.deepcopy(style or DEFAULT_STYLE)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plot(
        self,
        ax: Axes,
        compounds: list[CompoundHomoLumo],
        style: DiagramStyle,
    ) -> dict[str, Any]:
        """Render the HOMO/LUMO diagram onto *ax*.

        Clears the axes first, then draws all elements from scratch.

        Args:
            ax: The matplotlib Axes to draw on.
            compounds: List of compounds to render, in display order.
            style: Full style configuration dict.

        Returns:
            Dict of artist groups keyed by name (``"homo_lines"``,
            ``"lumo_lines"``, ``"arrows"``, ``"homo_texts"``,
            ``"lumo_texts"``, ``"gap_texts"``).
        """
        style = validate_style_fonts(style)
        ax.cla()
        logger.debug("Plotting %d compounds", len(compounds))

        if not compounds:
            ax.text(
                0.5, 0.5,
                "No data loaded",
                transform=ax.transAxes,
                ha="center", va="center",
                fontsize=14, color="#888888",
            )
            apply_axes_decorations(ax, style)
            return {}

        artists: dict[str, list[Any]] = {
            "homo_lines": [],
            "lumo_lines": [],
            "arrows": [],
            "homo_texts": [],
            "lumo_texts": [],
            "gap_texts": [],
        }
        artists_by_id: dict[str, Any] = {}

        homo_s = style["homo"]
        lumo_s = style["lumo"]
        gap_s = style["gap_arrow"]
        lbl_s = style["compound_labels"]

        # Compute y-gap for value label offset in data coordinates
        all_y = [c.homo for c in compounds] + [c.lumo for c in compounds]
        y_range = max(all_y) - min(all_y)
        y_gap = max(y_range * 0.04, 0.08)

        for i, compound in enumerate(compounds):
            self._draw_compound(
                ax, i, compound, homo_s, lumo_s, gap_s, lbl_s,
                artists, artists_by_id, y_gap,
            )

        self._apply_axes_style(ax, compounds, style)
        self._apply_legend(ax, homo_s, lumo_s, style["legend"])

        # Apply any user-dragged label position overrides
        for label_id, pos in style.get("label_overrides", {}).items():
            if label_id in artists_by_id:
                artists_by_id[label_id].set_position(tuple(pos))

        artists["by_id"] = artists_by_id
        return artists

    def update_style(self, style: DiagramStyle) -> None:
        """Store a new style dict.

        Full redraw is handled by the owning diagram widget; this method
        exists so the plotter always holds the latest style for reference.

        Args:
            style: The new style configuration.
        """
        self._style = style

    # ------------------------------------------------------------------
    # Internal drawing helpers
    # ------------------------------------------------------------------

    def _draw_compound(
        self,
        ax: Axes,
        i: int,
        compound: CompoundHomoLumo,
        homo_s: dict[str, Any],
        lumo_s: dict[str, Any],
        gap_s: dict[str, Any],
        lbl_s: dict[str, Any],
        artists: dict[str, list[Any]],
        artists_by_id: dict[str, Any],
        y_gap: float,
    ) -> None:
        x_left = i - _HALF_WIDTH
        x_right = i + _HALF_WIDTH

        # HOMO line
        (homo_line,) = ax.plot(
            [x_left, x_right],
            [compound.homo, compound.homo],
            color=homo_s["color"],
            linewidth=homo_s["linewidth"],
            solid_capstyle="butt",
        )
        artists["homo_lines"].append(homo_line)

        # LUMO line
        (lumo_line,) = ax.plot(
            [x_left, x_right],
            [compound.lumo, compound.lumo],
            color=lumo_s["color"],
            linewidth=lumo_s["linewidth"],
            solid_capstyle="butt",
        )
        artists["lumo_lines"].append(lumo_line)

        # HOMO value text — below the line (draggable, so ax.text not annotate)
        homo_text = ax.text(
            i, compound.homo - y_gap,
            homo_s["value_format"].format(compound.homo),
            ha="center",
            va="top",
            fontsize=homo_s["value_fontsize"],
            color=homo_s["value_color"],
            fontfamily=lbl_s["fontfamily"],
            clip_on=False,
        )
        artists["homo_texts"].append(homo_text)
        artists_by_id[f"homo_value_{i}"] = homo_text

        # LUMO value text — above the line
        lumo_text = ax.text(
            i, compound.lumo + y_gap,
            lumo_s["value_format"].format(compound.lumo),
            ha="center",
            va="bottom",
            fontsize=lumo_s["value_fontsize"],
            color=lumo_s["value_color"],
            fontfamily=lbl_s["fontfamily"],
            clip_on=False,
        )
        artists["lumo_texts"].append(lumo_text)
        artists_by_id[f"lumo_value_{i}"] = lumo_text

        # Double-headed gap arrow
        arrow = ax.annotate(
            "",
            xy=(i, compound.lumo),
            xytext=(i, compound.homo),
            arrowprops=dict(
                arrowstyle="<->",
                color=gap_s["color"],
                lw=gap_s["linewidth"],
            ),
        )
        artists["arrows"].append(arrow)

        # Gap value label — midpoint, offset right (draggable)
        mid_y = (compound.homo + compound.lumo) / 2.0
        gap_text = ax.text(
            i + _GAP_TEXT_OFFSET,
            mid_y,
            gap_s["format"].format(compound.gap),
            ha="left",
            va="center",
            fontsize=gap_s["fontsize"],
            color=gap_s["color"],
            fontfamily=lbl_s["fontfamily"],
            clip_on=False,
        )
        artists["gap_texts"].append(gap_text)
        artists_by_id[f"gap_{i}"] = gap_text

    def _apply_axes_style(
        self,
        ax: Axes,
        compounds: list[CompoundHomoLumo],
        style: DiagramStyle,
    ) -> None:
        # X ticks and compound name labels
        apply_x_ticks(ax, [c.name for c in compounds], style)

        # Y-axis limits with 15% margin so value annotations fit
        all_y = [c.homo for c in compounds] + [c.lumo for c in compounds]
        y_range = max(all_y) - min(all_y)
        margin = max(y_range * 0.15, 0.5)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

        # Apply all other axis decorations (labels, grid, spines, title, bg)
        apply_axes_decorations(ax, style)

    def _apply_legend(
        self,
        ax: Axes,
        homo_s: dict[str, Any],
        lumo_s: dict[str, Any],
        legend_s: dict[str, Any],
    ) -> None:
        if not legend_s["visible"]:
            return
        homo_handle = Line2D(
            [0], [0],
            color=homo_s["color"],
            linewidth=homo_s["linewidth"],
            label="HOMO",
        )
        lumo_handle = Line2D(
            [0], [0],
            color=lumo_s["color"],
            linewidth=lumo_s["linewidth"],
            label="LUMO",
        )
        ax.legend(
            handles=[homo_handle, lumo_handle],
            loc=legend_s["location"],
            fontsize=legend_s["fontsize"],
            frameon=legend_s["frameon"],
        )
