"""Shared plotting helpers used by multiple diagram plotters."""
from __future__ import annotations
import logging
from typing import Any
from matplotlib.axes import Axes
logger = logging.getLogger(__name__)

def apply_axes_decorations(ax: Axes, style: dict[str, Any]) -> None:
    """Apply non-data-dependent axis decorations shared by all plotters.

    Covers: ylabel, xlabel (if set), grid, spine linewidths, tick label
    sizes, title, and figure/axes background colour.

    Args:
        ax: The Axes to decorate.
        style: Full DiagramStyle dict.
    """
    axes_s = style["axes"]
    title_s = style["title"]

    ax.set_ylabel(
        axes_s["ylabel"],
        fontsize=axes_s["label_fontsize"],
        fontfamily=axes_s["label_fontfamily"],
    )
    if axes_s.get("xlabel"):
        ax.set_xlabel(
            axes_s["xlabel"],
            fontsize=axes_s["label_fontsize"],
            fontfamily=axes_s["label_fontfamily"],
        )

    ax.tick_params(axis="both", labelsize=axes_s["tick_fontsize"])

    for spine in ax.spines.values():
        spine.set_linewidth(axes_s["spine_linewidth"])

    if axes_s["show_grid"]:
        ax.grid(True, axis="y", alpha=axes_s["grid_alpha"], linestyle="--", color="#cccccc")
        ax.set_axisbelow(True)
    else:
        ax.grid(False)

    if title_s["visible"]:
        ax.set_title(
            title_s["text"],
            fontsize=title_s["fontsize"],
            fontfamily=title_s["fontfamily"],
            fontweight=title_s["fontweight"],
            color=title_s["color"],
        )

    bg = style["figure"]["background_color"]
    ax.set_facecolor(bg)
    if ax.figure is not None:
        ax.figure.set_facecolor(bg)


def apply_x_ticks(
    ax: Axes,
    names: list[str],
    style: dict[str, Any],
) -> None:
    """Set x-axis ticks and compound-name labels for a compound-indexed plot.

    Also sets xlim with a half-unit margin on each side.

    Args:
        ax: The Axes to configure.
        names: Compound names in display order.
        style: Full DiagramStyle dict.
    """
    n = len(names)
    lbl_s = style["compound_labels"]
    ax.set_xticks(list(range(n)))
    ax.set_xticklabels(
        names,
        fontsize=lbl_s["fontsize"],
        fontfamily=lbl_s["fontfamily"],
        rotation=lbl_s["rotation"],
        ha="center",
    )
    ax.set_xlim(-0.5, n - 0.5)
