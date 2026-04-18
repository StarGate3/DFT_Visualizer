"""Franck-Condon potential energy curve diagram widget."""
from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from src.data.models import DFTDataset
from src.gui.diagram_widgets.base_diagram import BaseDiagramWidget
from src.plotting.franck_condon_plot import FranckCondonPlotter

logger = logging.getLogger(__name__)


class FranckCondonDiagramWidget(BaseDiagramWidget):
    """Embeds a Franck-Condon potential energy diagram in the main tab area."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._plotter = FranckCondonPlotter()
        self._compound_names: list[str] = []

        # Extra controls row — fixed-height strip above the canvas
        controls = QWidget()
        controls.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        controls.setFixedHeight(40)
        row = QHBoxLayout(controls)
        row.setContentsMargins(4, 2, 4, 2)
        row.setSpacing(6)

        row.addWidget(QLabel("Compound:"))
        self._compound_combo = QComboBox()
        self._compound_combo.setMinimumWidth(150)
        self._compound_combo.setMaximumWidth(300)
        self._compound_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._compound_combo.currentIndexChanged.connect(self._on_control_changed)
        row.addWidget(self._compound_combo)

        row.addSpacing(16)
        row.addWidget(QLabel("Unit:"))
        self._unit_combo = QComboBox()
        self._unit_combo.addItems(["kcal/mol", "eV"])
        self._unit_combo.currentTextChanged.connect(self._on_control_changed)
        row.addWidget(self._unit_combo)
        row.addStretch(1)

        # Insert after nav toolbar (index 0); give canvas all remaining space
        layout = self.layout()
        layout.insertWidget(1, controls, 0)
        layout.setStretchFactor(self.canvas, 1)

    # ------------------------------------------------------------------
    # BaseDiagramWidget interface
    # ------------------------------------------------------------------

    def refresh(self, dataset: DFTDataset, style: dict) -> None:
        self._dataset = dataset
        self._style = style

        # Repopulate compound list if it changed
        names = sorted({e.name for e in dataset.franck_condon})
        if names != self._compound_names:
            self._compound_names = names
            self._compound_combo.blockSignals(True)
            self._compound_combo.clear()
            self._compound_combo.addItems(names)
            self._compound_combo.blockSignals(False)

        self._draw()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        if self._dataset is None or self._style is None:
            return

        selected = self._compound_combo.currentText()
        unit = self._unit_combo.currentText()
        entries = [e for e in self._dataset.franck_condon if e.name == selected]

        fig_s = self._style.get("figure", {})
        if "figsize" in fig_s:
            self.figure.set_size_inches(*fig_s["figsize"])

        self.figure.clear()
        self.figure.set_tight_layout(False)
        ax = self.figure.add_subplot(111)

        result = self._plotter.plot(ax, entries, self._style, unit, compound_name=selected)

        self.figure.subplots_adjust(left=0.04, right=0.88, top=0.92, bottom=0.04)

        # Register draggable label artists
        self._setup_drag_manager(result.get("by_id", {}))

        # Build clickable artist list for right-click context menus
        self._build_clickable_artists(result)

        self.canvas.draw_idle()

    def _build_clickable_artists(self, result: dict) -> None:
        self._clickable_artists = []
        by_id = result.get("by_id", {})

        # Text label metadata
        _text_meta = {
            "fc_s0_label": {"style_section": "fc_s0", "style_text_key": "label_text",
                            "style_color_key": "color", "style_size_key": "label_fontsize"},
            "fc_s1_label": {"style_section": "fc_s1", "style_text_key": "label_text",
                            "style_color_key": "color", "style_size_key": "label_fontsize"},
            "fc_t1_label": {"style_section": "fc_t1", "style_text_key": "label_text",
                            "style_color_key": "color", "style_size_key": "label_fontsize"},
            "fc_s1_vert":  {"style_section": "fc_s1", "style_color_key": "color",
                            "style_size_key": "value_fontsize"},
            "fc_s1_ad":    {"style_section": "fc_s1", "style_color_key": "color",
                            "style_size_key": "value_fontsize"},
            "fc_t1_ad":    {"style_section": "fc_t1", "style_color_key": "color",
                            "style_size_key": "value_fontsize"},
            "fc_isc_label": {"style_section": "fc_isc", "style_text_key": "label_text",
                             "style_color_key": "color", "style_size_key": "label_fontsize"},
        }
        for label_id, artist in by_id.items():
            base_meta = _text_meta.get(label_id, {})
            meta = {"label_id": label_id, **base_meta}
            self._clickable_artists.append((artist, "text", meta))

        # Morse curves
        curves = result.get("curves", {})
        for state, section in (("S0", "fc_s0"), ("S1", "fc_s1"), ("T1", "fc_t1")):
            curve = curves.get(state)
            if curve is not None:
                self._clickable_artists.append((curve, "line", {
                    "style_section": section,
                    "style_color_key": "color",
                    "style_lw_key": "linewidth",
                }))

        # Transition arrows
        transitions = result.get("transitions", {})
        vert = transitions.get("vertical")
        if vert is not None:
            self._clickable_artists.append((vert, "arrow", {
                "style_section": "fc_vertical_arrow",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
                "style_show_key": "show",
            }))
        adib = transitions.get("adiabatic")
        if adib is not None:
            self._clickable_artists.append((adib, "arrow", {
                "style_section": "fc_adiabatic_arrow",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
                "style_show_key": "show",
            }))

        # ISC arrow
        isc = result.get("isc", {})
        isc_arrow = isc.get("arrow")
        if isc_arrow is not None:
            self._clickable_artists.append((isc_arrow, "arrow", {
                "style_section": "fc_isc",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
                "style_show_key": "show",
            }))

    def get_selected_compound(self) -> str:
        return self._compound_combo.currentText()

    def get_selected_unit(self) -> str:
        return self._unit_combo.currentText()

    def _on_control_changed(self, _: object = None) -> None:
        self._draw()
