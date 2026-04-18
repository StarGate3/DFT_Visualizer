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

    def export_figure(
        self,
        filepath: Path,
        dpi: int,
        fmt: str,
        figsize_cm: Optional[tuple[float, float]],
        background: str,
        tiff_compression: str = "lzw",
    ) -> None:
        """Save the figure to *filepath* with publication-quality settings.

        Args:
            filepath: Destination file path.
            dpi: Resolution in DPI (ignored by matplotlib for vector formats).
            fmt: Format string — 'png', 'tiff', 'svg', or 'pdf'.
            figsize_cm: (width, height) in centimetres; None keeps current size.
            background: 'transparent', 'white', or 'style' (use figure colour).
            tiff_compression: 'lzw', 'deflate', or 'none' (TIFF only).
        """
        orig_size = self.figure.get_size_inches()
        try:
            if figsize_cm is not None:
                self.figure.set_size_inches(
                    figsize_cm[0] / 2.54, figsize_cm[1] / 2.54
                )

            if background == "transparent":
                facecolor: object = (0.0, 0.0, 0.0, 0.0)
            elif background == "white":
                facecolor = "white"
            else:
                facecolor = self.figure.get_facecolor()

            kwargs: dict = {
                "format": fmt,
                "dpi": dpi,
                "bbox_inches": "tight",
                "facecolor": facecolor,
                "edgecolor": "none",
            }
            if fmt.lower() == "tiff":
                _compression_map = {
                    "lzw": "tiff_lzw",
                    "deflate": "tiff_deflate",
                    "none": "raw",
                }
                kwargs["pil_kwargs"] = {
                    "compression": _compression_map.get(tiff_compression, "tiff_lzw")
                }

            logger.debug("Exporting %s → %s at %d DPI", fmt.upper(), filepath, dpi)
            self.figure.savefig(filepath, **kwargs)
        finally:
            self.figure.set_size_inches(*orig_size)
            self.canvas.draw_idle()
