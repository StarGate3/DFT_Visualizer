"""Shared plotting helpers used by multiple diagram plotters."""
from __future__ import annotations
import copy
import logging
from typing import Any
from matplotlib import font_manager as _mpl_fm
from matplotlib.axes import Axes

logger = logging.getLogger(__name__)

_FALLBACK_FONT = "DejaVu Sans"
KCAL_PER_EV: float = 23.0605


def convert_energy(value: float, from_unit: str, to_unit: str) -> float:
    """Convert energy between 'eV' and 'kcal/mol'."""
    if from_unit == to_unit:
        return value
    if from_unit == "eV" and to_unit == "kcal/mol":
        return value * KCAL_PER_EV
    if from_unit == "kcal/mol" and to_unit == "eV":
        return value / KCAL_PER_EV
    raise ValueError(f"Unknown unit conversion: {from_unit!r} -> {to_unit!r}")


def _is_font_available(name: str) -> bool:
    try:
        _mpl_fm.findfont(name, fallback_to_default=False)
        return True
    except Exception:
        return False


def validate_style_fonts(style: dict[str, Any]) -> dict[str, Any]:
    """Return *style* with font fields substituted if the requested font is unavailable.

    Makes a deep copy only when a substitution is needed, so the common
    (no-substitution) path is allocation-free.
    """
    font = style.get("title", {}).get("fontfamily", _FALLBACK_FONT)
    if _is_font_available(font):
        return style
    logger.warning("Font '%s' not available for plot; using %s", font, _FALLBACK_FONT)
    style = copy.deepcopy(style)
    style["title"]["fontfamily"] = _FALLBACK_FONT
    style["axes"]["label_fontfamily"] = _FALLBACK_FONT
    style["compound_labels"]["fontfamily"] = _FALLBACK_FONT
    return style

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
        grid_color = axes_s.get("grid_color", "#cccccc")
        ax.grid(True, axis="y", alpha=axes_s["grid_alpha"], linestyle="--", color=grid_color)
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
