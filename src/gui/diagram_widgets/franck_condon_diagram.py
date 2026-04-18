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
    """Embeds a Franck-Condon potential energy diagram in the main tab area.

    Provides a compound selector and unit selector in a toolbar row above
    the matplotlib canvas.  Calls :class:`FranckCondonPlotter` for rendering.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._plotter = FranckCondonPlotter()
        self._compound_names: list[str] = []
        self._dataset: Optional[DFTDataset] = None
        self._style: Optional[dict] = None

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
        layout.insertWidget(1, controls, 0)       # stretch=0: stays at fixed height
        layout.setStretchFactor(self.canvas, 1)   # stretch=1: canvas fills the rest

    # ------------------------------------------------------------------
    # BaseDiagramWidget interface
    # ------------------------------------------------------------------

    def refresh(self, dataset: DFTDataset, style: dict) -> None:
        """Re-render the diagram.

        Args:
            dataset: Current DFT dataset; only ``franck_condon`` entries are used.
            style: DiagramStyle dict from the StylePanel.
        """
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

        self._plotter.plot(ax, entries, self._style, unit, compound_name=selected)
        self.figure.subplots_adjust(left=0.04, right=0.88, top=0.92, bottom=0.04)
        self.canvas.draw_idle()

    def _on_control_changed(self, _: object = None) -> None:
        self._draw()
