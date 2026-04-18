"""HOMO/LUMO energy level diagram widget."""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtWidgets import QWidget

from src.data.models import DFTDataset
from src.gui.diagram_widgets.base_diagram import BaseDiagramWidget
from src.plotting.homo_lumo_plot import HomoLumoPlotter
from src.plotting.style_presets import DEFAULT_STYLE, DiagramStyle

logger = logging.getLogger(__name__)


class HomoLumoDiagramWidget(BaseDiagramWidget):
    """Embeds a HOMO/LUMO energy level diagram in the main tab area.

    Uses :class:`~src.plotting.homo_lumo_plot.HomoLumoPlotter` for all
    rendering.  Displays a "No data loaded" message when the dataset is empty.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._plotter = HomoLumoPlotter()

    # ------------------------------------------------------------------
    # BaseDiagramWidget interface
    # ------------------------------------------------------------------

    def refresh(self, dataset: DFTDataset, style: dict) -> None:
        """Re-render the diagram.

        Args:
            dataset: Current DFT dataset; only ``homo_lumo`` entries are used.
            style: DiagramStyle dict from the StylePanel.
        """
        compounds = dataset.homo_lumo
        logger.debug("HomoLumoDiagramWidget.refresh: %d compounds", len(compounds))

        # Apply figure size from style (does not affect screen DPI — preview
        # always uses the figure's default DPI for crisp on-screen rendering).
        fig_s = style.get("figure", {})
        if "figsize" in fig_s:
            self.figure.set_size_inches(*fig_s["figsize"])

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        self._plotter.update_style(style)
        self._plotter.plot(ax, compounds, style)

        self.canvas.draw_idle()
