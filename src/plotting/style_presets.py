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


class FCStateStyle(TypedDict):
    """Style for one FC potential energy curve (S0, S1, or T1)."""
    color: str
    linewidth: float
    label_text: str
    label_fontsize: int
    value_fontsize: int
    r_eq: float
    k_factor: float


class FCArrowStyle(TypedDict):
    """Style for the vertical Franck-Condon arrow."""
    color: str
    linewidth: float
    arrow_style: str
    show: bool


class FCAdiabArrowStyle(TypedDict):
    """Style for the dashed adiabatic-transition arrow."""
    color: str
    linewidth: float
    arrow_style: str
    show: bool
    linestyle: str


class FCGuideLinesStyle(TypedDict):
    color: str
    linewidth: float
    linestyle: str
    alpha: float
    show: bool


class FCIscStyle(TypedDict):
    """Style for the ISC curved arrow on the FC diagram."""
    color: str
    linewidth: float
    show: bool
    show_label: bool
    label_text: str
    label_fontsize: int


class FCAxesStyle(TypedDict):
    color: str
    linewidth: float
    ylabel_text: str
    ylabel_fontsize: int
    xlabel_text: str
    xlabel_fontsize: int


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
    fc_s0: FCStateStyle
    fc_s1: FCStateStyle
    fc_t1: FCStateStyle
    fc_vertical_arrow: FCArrowStyle
    fc_adiabatic_arrow: FCAdiabArrowStyle
    fc_guide_lines: FCGuideLinesStyle
    fc_isc: FCIscStyle
    fc_axes: FCAxesStyle


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
        "fontsize": 15,
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
    "fc_s0": {"color": "#1F3C7A", "linewidth": 1.8, "label_text": "$S_0$", "label_fontsize": 14, "value_fontsize": 10, "r_eq": 0.0, "k_factor": 1.0},
    "fc_s1": {"color": "#3A5FCD", "linewidth": 1.8, "label_text": "$S_1$", "label_fontsize": 14, "value_fontsize": 10, "r_eq": 0.5, "k_factor": 1.0},
    "fc_t1": {"color": "#2E8B57", "linewidth": 1.8, "label_text": "$T_1$", "label_fontsize": 14, "value_fontsize": 10, "r_eq": 0.3, "k_factor": 1.0},
    "fc_vertical_arrow": {"color": "#3A5FCD", "linewidth": 1.8, "arrow_style": "-|>", "show": True},
    "fc_adiabatic_arrow": {"color": "#3A5FCD", "linewidth": 1.5, "arrow_style": "-|>", "show": True, "linestyle": "dashed"},
    "fc_guide_lines": {"color": "#888888", "linewidth": 0.5, "linestyle": "dotted", "alpha": 0.6, "show": True},
    "fc_isc": {"color": "#666666", "linewidth": 1.3, "show": True, "show_label": True, "label_text": "ISC", "label_fontsize": 10},
    "fc_axes": {"color": "#333333", "linewidth": 1.3, "ylabel_text": "Energy", "ylabel_fontsize": 12, "xlabel_text": "Reaction coordinate (r)", "xlabel_fontsize": 11},
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
    "fc_s0": {"color": "#1F3C7A", "linewidth": 1.2, "label_text": "S0", "label_fontsize": 10, "value_fontsize": 8, "r_eq": 0.0, "k_factor": 1.0},
    "fc_s1": {"color": "#3D71CC", "linewidth": 1.2, "label_text": "S1", "label_fontsize": 10, "value_fontsize": 8, "r_eq": 0.5, "k_factor": 1.0},
    "fc_t1": {"color": "#E08A2D", "linewidth": 1.2, "label_text": "T1", "label_fontsize": 10, "value_fontsize": 8, "r_eq": 0.3, "k_factor": 1.0},
    "fc_vertical_arrow": {"color": "#1F3C7A", "linewidth": 1.0, "arrow_style": "-|>", "show": True},
    "fc_adiabatic_arrow": {"color": "#1F3C7A", "linewidth": 1.0, "arrow_style": "-|>", "show": True, "linestyle": "dashed"},
    "fc_guide_lines": {"color": "#888888", "linewidth": 0.5, "linestyle": "dotted", "alpha": 0.6, "show": True},
    "fc_isc": {"color": "#555555", "linewidth": 1.0, "show": True, "show_label": True, "label_text": "ISC", "label_fontsize": 8},
    "fc_axes": {"color": "#333333", "linewidth": 1.0, "ylabel_text": "Energy", "ylabel_fontsize": 11, "xlabel_text": "Reaction coordinate (r)", "xlabel_fontsize": 10},
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
    "fc_s0": {"color": "#0072B2", "linewidth": 1.8, "label_text": "S0", "label_fontsize": 11, "value_fontsize": 9, "r_eq": 0.0, "k_factor": 1.0},
    "fc_s1": {"color": "#56B4E9", "linewidth": 1.8, "label_text": "S1", "label_fontsize": 11, "value_fontsize": 9, "r_eq": 0.5, "k_factor": 1.0},
    "fc_t1": {"color": "#D55E00", "linewidth": 1.8, "label_text": "T1", "label_fontsize": 11, "value_fontsize": 9, "r_eq": 0.3, "k_factor": 1.0},
    "fc_vertical_arrow": {"color": "#0072B2", "linewidth": 1.5, "arrow_style": "-|>", "show": True},
    "fc_adiabatic_arrow": {"color": "#0072B2", "linewidth": 1.2, "arrow_style": "-|>", "show": True, "linestyle": "dashed"},
    "fc_guide_lines": {"color": "#888888", "linewidth": 0.5, "linestyle": "dotted", "alpha": 0.6, "show": True},
    "fc_isc": {"color": "#555555", "linewidth": 1.3, "show": True, "show_label": True, "label_text": "ISC", "label_fontsize": 9},
    "fc_axes": {"color": "#333333", "linewidth": 1.0, "ylabel_text": "Energy", "ylabel_fontsize": 11, "xlabel_text": "Reaction coordinate (r)", "xlabel_fontsize": 10},
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
    "fc_s0": {"color": "#000000", "linewidth": 1.5, "label_text": "S0", "label_fontsize": 10, "value_fontsize": 8, "r_eq": 0.0, "k_factor": 1.0},
    "fc_s1": {"color": "#444444", "linewidth": 1.5, "label_text": "S1", "label_fontsize": 10, "value_fontsize": 8, "r_eq": 0.5, "k_factor": 1.0},
    "fc_t1": {"color": "#888888", "linewidth": 1.5, "label_text": "T1", "label_fontsize": 10, "value_fontsize": 8, "r_eq": 0.3, "k_factor": 1.0},
    "fc_vertical_arrow": {"color": "#000000", "linewidth": 1.0, "arrow_style": "-|>", "show": True},
    "fc_adiabatic_arrow": {"color": "#000000", "linewidth": 1.0, "arrow_style": "-|>", "show": True, "linestyle": "dashed"},
    "fc_guide_lines": {"color": "#888888", "linewidth": 0.5, "linestyle": "dotted", "alpha": 0.6, "show": True},
    "fc_isc": {"color": "#000000", "linewidth": 1.2, "show": True, "show_label": True, "label_text": "ISC", "label_fontsize": 9},
    "fc_axes": {"color": "#333333", "linewidth": 1.0, "ylabel_text": "Energy", "ylabel_fontsize": 11, "xlabel_text": "Reaction coordinate (r)", "xlabel_fontsize": 10},
}

def _make_publication_high_dpi() -> DiagramStyle:
    """Build the Publication High-DPI preset from PUBLICATION_STYLE."""
    p = copy.deepcopy(PUBLICATION_STYLE)
    p["title"]["fontsize"] = 14
    p["title"]["fontfamily"] = "Arial"
    p["figure"]["dpi"] = 600
    p["homo"]["linewidth"] = 2.0
    p["homo"]["value_fontsize"] = 10
    p["lumo"]["linewidth"] = 2.0
    p["lumo"]["value_fontsize"] = 10
    p["gap_arrow"]["linewidth"] = 1.5
    p["gap_arrow"]["fontsize"] = 10
    p["s0"]["linewidth"] = 2.0
    p["s0"]["value_fontsize"] = 10
    p["s0"]["label_fontsize"] = 13
    p["s1"]["linewidth"] = 2.0
    p["s1"]["value_fontsize"] = 10
    p["s1"]["label_fontsize"] = 13
    p["t1"]["linewidth"] = 2.0
    p["t1"]["value_fontsize"] = 10
    p["t1"]["label_fontsize"] = 13
    p["absorption_arrow"]["linewidth"] = 1.8
    p["absorption_arrow"]["label_fontsize"] = 10
    p["isc_curve"]["linewidth"] = 1.5
    p["isc_curve"]["label_fontsize"] = 10
    p["fc_s0"]["linewidth"] = 2.4
    p["fc_s0"]["label_fontsize"] = 13
    p["fc_s0"]["value_fontsize"] = 10
    p["fc_s1"]["linewidth"] = 2.4
    p["fc_s1"]["label_fontsize"] = 13
    p["fc_s1"]["value_fontsize"] = 10
    p["fc_t1"]["linewidth"] = 2.4
    p["fc_t1"]["label_fontsize"] = 13
    p["fc_t1"]["value_fontsize"] = 10
    p["fc_vertical_arrow"]["linewidth"] = 2.0
    p["fc_adiabatic_arrow"]["linewidth"] = 1.8
    p["fc_isc"]["linewidth"] = 1.6
    p["fc_isc"]["label_fontsize"] = 10
    p["fc_axes"]["linewidth"] = 1.5
    p["fc_axes"]["ylabel_fontsize"] = 12
    p["fc_axes"]["xlabel_fontsize"] = 11
    return p  # type: ignore[return-value]


PUBLICATION_HIGH_DPI_STYLE: DiagramStyle = _make_publication_high_dpi()


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_PRESETS: dict[str, DiagramStyle] = {
    "Default": DEFAULT_STYLE,
    "Publication": PUBLICATION_STYLE,
    "Publication High-DPI": PUBLICATION_HIGH_DPI_STYLE,
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
