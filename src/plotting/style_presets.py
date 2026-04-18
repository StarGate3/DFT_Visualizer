"""Color and style presets for DFT diagrams."""

from __future__ import annotations

import copy
from typing import TypedDict


# ---------------------------------------------------------------------------
# TypedDict hierarchy
# ---------------------------------------------------------------------------


class FigureStyle(TypedDict):
    background_color: str
    figsize: tuple[float, float]
    dpi: int


class TitleStyle(TypedDict):
    text: str
    fontsize: int
    fontfamily: str
    fontweight: str
    color: str
    visible: bool


class AxesStyle(TypedDict):
    xlabel: str
    ylabel: str
    label_fontsize: int
    label_fontfamily: str
    tick_fontsize: int
    spine_linewidth: float
    show_grid: bool
    grid_alpha: float


class LineStyle(TypedDict):
    """Style for HOMO or LUMO horizontal line segments."""
    color: str
    linewidth: float
    marker_style: str
    value_fontsize: int
    value_color: str
    value_format: str
    value_offset_points: int  # vertical offset of value label in points; neg = below


class GapArrowStyle(TypedDict):
    color: str
    linewidth: float
    arrow_style: str
    fontsize: int
    format: str


class CompoundLabelsStyle(TypedDict):
    fontsize: int
    fontfamily: str
    rotation: int


class LegendStyle(TypedDict):
    visible: bool
    location: str
    fontsize: int
    frameon: bool


class DiagramStyle(TypedDict):
    figure: FigureStyle
    title: TitleStyle
    axes: AxesStyle
    homo: LineStyle
    lumo: LineStyle
    gap_arrow: GapArrowStyle
    compound_labels: CompoundLabelsStyle
    legend: LegendStyle


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

DEFAULT_STYLE: DiagramStyle = {
    "figure": {
        "background_color": "#ffffff",
        "figsize": (10.0, 5.5),
        "dpi": 100,
    },
    "title": {
        "text": "Molecular Energy Diagram",
        "fontsize": 14,
        "fontfamily": "DejaVu Sans",
        "fontweight": "bold",
        "color": "#000000",
        "visible": True,
    },
    "axes": {
        "xlabel": "",
        "ylabel": "Energy (eV)",
        "label_fontsize": 11,
        "label_fontfamily": "DejaVu Sans",
        "tick_fontsize": 10,
        "spine_linewidth": 1.5,
        "show_grid": True,
        "grid_alpha": 0.3,
    },
    "homo": {
        "color": "#CC0000",
        "linewidth": 2.0,
        "marker_style": "none",
        "value_fontsize": 9,
        "value_color": "#CC0000",
        "value_format": "{:.2f} eV",
        "value_offset_points": -8,
    },
    "lumo": {
        "color": "#0044CC",
        "linewidth": 2.0,
        "marker_style": "none",
        "value_fontsize": 9,
        "value_color": "#0044CC",
        "value_format": "{:.2f} eV",
        "value_offset_points": 8,
    },
    "gap_arrow": {
        "color": "#444444",
        "linewidth": 1.0,
        "arrow_style": "<->",
        "fontsize": 9,
        "format": "{:.2f} eV",
    },
    "compound_labels": {
        "fontsize": 10,
        "fontfamily": "DejaVu Sans",
        "rotation": 0,
    },
    "legend": {
        "visible": True,
        "location": "upper right",
        "fontsize": 9,
        "frameon": True,
    },
}

PUBLICATION_STYLE: DiagramStyle = {
    "figure": {
        "background_color": "#ffffff",
        "figsize": (10.0, 5.0),
        "dpi": 300,
    },
    "title": {
        "text": "Molecular Energy Diagram",
        "fontsize": 12,
        "fontfamily": "Arial",
        "fontweight": "bold",
        "color": "#000000",
        "visible": True,
    },
    "axes": {
        "xlabel": "",
        "ylabel": "Energy (eV)",
        "label_fontsize": 10,
        "label_fontfamily": "Arial",
        "tick_fontsize": 9,
        "spine_linewidth": 1.0,
        "show_grid": False,
        "grid_alpha": 0.0,
    },
    "homo": {
        "color": "#CC0000",
        "linewidth": 1.0,
        "marker_style": "none",
        "value_fontsize": 8,
        "value_color": "#CC0000",
        "value_format": "{:.2f} eV",
        "value_offset_points": -8,
    },
    "lumo": {
        "color": "#0044CC",
        "linewidth": 1.0,
        "marker_style": "none",
        "value_fontsize": 8,
        "value_color": "#0044CC",
        "value_format": "{:.2f} eV",
        "value_offset_points": 8,
    },
    "gap_arrow": {
        "color": "#333333",
        "linewidth": 0.75,
        "arrow_style": "<->",
        "fontsize": 8,
        "format": "{:.2f} eV",
    },
    "compound_labels": {
        "fontsize": 9,
        "fontfamily": "Arial",
        "rotation": 0,
    },
    "legend": {
        "visible": True,
        "location": "upper right",
        "fontsize": 8,
        "frameon": False,
    },
}

# Okabe-Ito colorblind-safe palette
COLORBLIND_STYLE: DiagramStyle = {
    "figure": {
        "background_color": "#ffffff",
        "figsize": (10.0, 5.5),
        "dpi": 100,
    },
    "title": {
        "text": "Molecular Energy Diagram",
        "fontsize": 14,
        "fontfamily": "DejaVu Sans",
        "fontweight": "bold",
        "color": "#000000",
        "visible": True,
    },
    "axes": {
        "xlabel": "",
        "ylabel": "Energy (eV)",
        "label_fontsize": 11,
        "label_fontfamily": "DejaVu Sans",
        "tick_fontsize": 10,
        "spine_linewidth": 1.5,
        "show_grid": True,
        "grid_alpha": 0.3,
    },
    "homo": {
        "color": "#D55E00",   # Okabe-Ito vermillion
        "linewidth": 2.5,
        "marker_style": "none",
        "value_fontsize": 9,
        "value_color": "#D55E00",
        "value_format": "{:.2f} eV",
        "value_offset_points": -8,
    },
    "lumo": {
        "color": "#0072B2",   # Okabe-Ito sky blue
        "linewidth": 2.5,
        "marker_style": "none",
        "value_fontsize": 9,
        "value_color": "#0072B2",
        "value_format": "{:.2f} eV",
        "value_offset_points": 8,
    },
    "gap_arrow": {
        "color": "#444444",
        "linewidth": 1.0,
        "arrow_style": "<->",
        "fontsize": 9,
        "format": "{:.2f} eV",
    },
    "compound_labels": {
        "fontsize": 10,
        "fontfamily": "DejaVu Sans",
        "rotation": 0,
    },
    "legend": {
        "visible": True,
        "location": "upper right",
        "fontsize": 9,
        "frameon": True,
    },
}

GRAYSCALE_STYLE: DiagramStyle = {
    "figure": {
        "background_color": "#ffffff",
        "figsize": (10.0, 5.0),
        "dpi": 300,
    },
    "title": {
        "text": "Molecular Energy Diagram",
        "fontsize": 12,
        "fontfamily": "Arial",
        "fontweight": "bold",
        "color": "#000000",
        "visible": True,
    },
    "axes": {
        "xlabel": "",
        "ylabel": "Energy (eV)",
        "label_fontsize": 10,
        "label_fontfamily": "Arial",
        "tick_fontsize": 9,
        "spine_linewidth": 1.0,
        "show_grid": False,
        "grid_alpha": 0.0,
    },
    "homo": {
        "color": "#000000",
        "linewidth": 2.0,
        "marker_style": "none",
        "value_fontsize": 8,
        "value_color": "#000000",
        "value_format": "{:.2f} eV",
        "value_offset_points": -8,
    },
    "lumo": {
        "color": "#555555",
        "linewidth": 2.0,
        "marker_style": "none",
        "value_fontsize": 8,
        "value_color": "#555555",
        "value_format": "{:.2f} eV",
        "value_offset_points": 8,
    },
    "gap_arrow": {
        "color": "#333333",
        "linewidth": 0.75,
        "arrow_style": "<->",
        "fontsize": 8,
        "format": "{:.2f} eV",
    },
    "compound_labels": {
        "fontsize": 9,
        "fontfamily": "Arial",
        "rotation": 0,
    },
    "legend": {
        "visible": True,
        "location": "upper right",
        "fontsize": 8,
        "frameon": False,
    },
}

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_PRESETS: dict[str, DiagramStyle] = {
    "Default": DEFAULT_STYLE,
    "Publication": PUBLICATION_STYLE,
    "Colorblind-safe": COLORBLIND_STYLE,
    "Grayscale": GRAYSCALE_STYLE,
}


def list_presets() -> list[str]:
    """Return the names of all available style presets."""
    return list(_PRESETS.keys())


def get_preset(name: str) -> DiagramStyle:
    """Return a deep copy of the named preset.

    Args:
        name: One of the strings returned by :func:`list_presets`.

    Returns:
        A fresh copy of the preset dict so callers can mutate it freely.

    Raises:
        KeyError: If *name* is not a known preset.
    """
    if name not in _PRESETS:
        raise KeyError(f"Unknown preset '{name}'. Available: {list_presets()}")
    return copy.deepcopy(_PRESETS[name])
