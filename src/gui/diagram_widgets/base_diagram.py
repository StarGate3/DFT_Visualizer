"""Abstract base class for all diagram widgets."""

from __future__ import annotations

import logging
from abc import abstractmethod
from pathlib import Path
from typing import Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.data.models import DFTDataset

logger = logging.getLogger(__name__)


class BaseDiagramWidget(QWidget):
    """Base class for HOMO/LUMO, States, and Franck-Condon diagram widgets.

    Owns the matplotlib Figure + FigureCanvasQTAgg and the navigation toolbar.
    Subclasses implement :meth:`refresh` to render their specific diagram type.

    Signals:
        style_interaction: Emitted when the user interacts with a plot artist
            (reserved for Stage 6 drag-and-drop label repositioning).
    """

    style_interaction = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.figure = Figure(tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def refresh(self, dataset: DFTDataset, style: dict) -> None:
        """Re-render the diagram using *dataset* and *style*.

        Args:
            dataset: Current DFT data to visualise.
            style: DiagramStyle dict controlling all visual properties.
        """

    # ------------------------------------------------------------------
    # Export (full implementation comes in Stage 6)
    # ------------------------------------------------------------------

    def export_figure(self, filepath: Path, dpi: int = 300) -> None:
        """Save the current figure to *filepath* at the given *dpi*.

        Args:
            filepath: Destination path (extension determines format).
            dpi: Output resolution in dots per inch.
        """
        logger.debug("Exporting figure to %s at %d DPI", filepath, dpi)
        self.figure.savefig(filepath, dpi=dpi, bbox_inches="tight")
