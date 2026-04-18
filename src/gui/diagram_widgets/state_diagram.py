"""S0/S1/T1 state energy diagram widget."""
from __future__ import annotations
import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget
from src.data.models import DFTDataset
from src.gui.diagram_widgets.base_diagram import BaseDiagramWidget
from src.plotting.state_plot import StateDiagramPlotter
from src.plotting.style_presets import DEFAULT_STYLE, DiagramStyle

logger = logging.getLogger(__name__)


class StateDiagramWidget(BaseDiagramWidget):
    """Embeds a S0/S1/T1 state energy level diagram in the main tab area."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._plotter = StateDiagramPlotter()

    def refresh(self, dataset: DFTDataset, style: dict) -> None:
        """Re-render the state diagram.

        Args:
            dataset: Current DFT dataset; only ``states`` entries are used.
            style: DiagramStyle dict from the StylePanel.
        """
        compounds = dataset.states
        logger.debug("StateDiagramWidget.refresh: %d compounds", len(compounds))

        fig_s = style.get("figure", {})
        if "figsize" in fig_s:
            self.figure.set_size_inches(*fig_s["figsize"])

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self._plotter.update_style(style)
        self._plotter.plot(ax, compounds, style)
        self.canvas.draw_idle()
