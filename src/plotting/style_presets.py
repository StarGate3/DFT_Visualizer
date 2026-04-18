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


class StateLevelStyle(TypedDict):
    """Style for S0, S1, or T1 horizontal energy-level line."""
    color: str
    linewidth: float
    value_fontsize: int
    value_color: str
    value_format: str
    value_offset_points: int
    label_text: str
    label_fontsize: int
    label_fontweight: str
    label_color: str


class AbsorptionArrowStyle(TypedDict):
    color: str
    linewidth: float
    arrow_style: str
    label_text: str
    label_fontsize: int
    label_color: str
    show_label: bool


class IscCurveStyle(TypedDict):
    color: str
    linewidth: float
    linestyle: str
    label_text: str
    label_fontsize: int
    label_color: str
    show_label: bool
    curvature: float


class DiagramStyle(TypedDict):
    figure: FigureStyle
    title: TitleStyle
    axes: AxesStyle
    homo: LineStyle
    lumo: LineStyle
    gap_arrow: GapArrowStyle
    compound_labels: CompoundLabelsStyle
    legend: LegendStyle
    s0: StateLevelStyle
    s1: StateLevelStyle
    t1: StateLevelStyle
    absorption_arrow: AbsorptionArrowStyle
    isc_curve: IscCurveStyle


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
    "s0": {"color": "#1F2E5C", "linewidth": 2.5, "value_fontsize": 9, "value_color": "#1F2E5C", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S0", "label_fontsize": 10, "label_fontweight": "bold", "label_color": "#1F2E5C"},
    "s1": {"color": "#8B2E3C", "linewidth": 2.5, "value_fontsize": 9, "value_color": "#8B2E3C", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S1", "label_fontsize": 10, "label_fontweight": "bold", "label_color": "#8B2E3C"},
    "t1": {"color": "#2E6B3C", "linewidth": 2.5, "value_fontsize": 9, "value_color": "#2E6B3C", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "T1", "label_fontsize": 10, "label_fontweight": "bold", "label_color": "#2E6B3C"},
    "absorption_arrow": {"color": "#333333", "linewidth": 1.5, "arrow_style": "-|>", "label_text": "Abs.", "label_fontsize": 9, "label_color": "#333333", "show_label": True},
    "isc_curve": {"color": "#555555", "linewidth": 1.2, "linestyle": "dashed", "label_text": "ISC", "label_fontsize": 9, "label_color": "#555555", "show_label": True, "curvature": 0.3},
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
    "s0": {"color": "#1F2E5C", "linewidth": 1.0, "value_fontsize": 8, "value_color": "#1F2E5C", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S0", "label_fontsize": 9, "label_fontweight": "bold", "label_color": "#1F2E5C"},
    "s1": {"color": "#8B2E3C", "linewidth": 1.0, "value_fontsize": 8, "value_color": "#8B2E3C", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S1", "label_fontsize": 9, "label_fontweight": "bold", "label_color": "#8B2E3C"},
    "t1": {"color": "#2E6B3C", "linewidth": 1.0, "value_fontsize": 8, "value_color": "#2E6B3C", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "T1", "label_fontsize": 9, "label_fontweight": "bold", "label_color": "#2E6B3C"},
    "absorption_arrow": {"color": "#333333", "linewidth": 1.0, "arrow_style": "-|>", "label_text": "Abs.", "label_fontsize": 8, "label_color": "#333333", "show_label": True},
    "isc_curve": {"color": "#555555", "linewidth": 0.75, "linestyle": "dashed", "label_text": "ISC", "label_fontsize": 8, "label_color": "#555555", "show_label": True, "curvature": 0.3},
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
    "s0": {"color": "#0072B2", "linewidth": 2.5, "value_fontsize": 9, "value_color": "#0072B2", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S0", "label_fontsize": 10, "label_fontweight": "bold", "label_color": "#0072B2"},
    "s1": {"color": "#D55E00", "linewidth": 2.5, "value_fontsize": 9, "value_color": "#D55E00", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S1", "label_fontsize": 10, "label_fontweight": "bold", "label_color": "#D55E00"},
    "t1": {"color": "#009E73", "linewidth": 2.5, "value_fontsize": 9, "value_color": "#009E73", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "T1", "label_fontsize": 10, "label_fontweight": "bold", "label_color": "#009E73"},
    "absorption_arrow": {"color": "#333333", "linewidth": 1.5, "arrow_style": "-|>", "label_text": "Abs.", "label_fontsize": 9, "label_color": "#333333", "show_label": True},
    "isc_curve": {"color": "#555555", "linewidth": 1.2, "linestyle": "dashed", "label_text": "ISC", "label_fontsize": 9, "label_color": "#555555", "show_label": True, "curvature": 0.3},
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
    "s0": {"color": "#000000", "linewidth": 2.0, "value_fontsize": 8, "value_color": "#000000", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S0", "label_fontsize": 9, "label_fontweight": "bold", "label_color": "#000000"},
    "s1": {"color": "#333333", "linewidth": 2.0, "value_fontsize": 8, "value_color": "#333333", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "S1", "label_fontsize": 9, "label_fontweight": "bold", "label_color": "#333333"},
    "t1": {"color": "#666666", "linewidth": 2.0, "value_fontsize": 8, "value_color": "#666666", "value_format": "{:.2f} eV", "value_offset_points": 10, "label_text": "T1", "label_fontsize": 9, "label_fontweight": "bold", "label_color": "#666666"},
    "absorption_arrow": {"color": "#000000", "linewidth": 1.0, "arrow_style": "-|>", "label_text": "Abs.", "label_fontsize": 8, "label_color": "#000000", "show_label": True},
    "isc_curve": {"color": "#333333", "linewidth": 0.75, "linestyle": "dashed", "label_text": "ISC", "label_fontsize": 8, "label_color": "#333333", "show_label": True, "curvature": 0.3},
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
