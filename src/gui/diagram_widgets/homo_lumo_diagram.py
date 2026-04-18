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
    """Embeds a HOMO/LUMO energy level diagram in the main tab area."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._plotter = HomoLumoPlotter()

    # ------------------------------------------------------------------
    # BaseDiagramWidget interface
    # ------------------------------------------------------------------

    def refresh(self, dataset: DFTDataset, style: dict) -> None:
        self._dataset = dataset
        self._style = style
        self._draw()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        if self._dataset is None or self._style is None:
            return
        compounds = self._dataset.homo_lumo
        logger.debug("HomoLumoDiagramWidget._draw: %d compounds", len(compounds))

        fig_s = self._style.get("figure", {})
        if "figsize" in fig_s:
            self.figure.set_size_inches(*fig_s["figsize"])

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        self._plotter.update_style(self._style)
        result = self._plotter.plot(ax, compounds, self._style)

        # Register draggable label artists
        self._setup_drag_manager(result.get("by_id", {}))

        # Build clickable artist list for right-click context menus
        self._build_clickable_artists(result, compounds)

        self.canvas.draw_idle()

    def _build_clickable_artists(self, result: dict, compounds: list) -> None:
        self._clickable_artists = []
        by_id = result.get("by_id", {})

        for label_id, artist in by_id.items():
            if label_id.startswith("homo_value_"):
                self._clickable_artists.append((artist, "text", {
                    "label_id": label_id,
                    "style_section": "homo",
                    "style_text_key": "value_format",
                    "style_color_key": "value_color",
                    "style_size_key": "value_fontsize",
                }))
            elif label_id.startswith("lumo_value_"):
                self._clickable_artists.append((artist, "text", {
                    "label_id": label_id,
                    "style_section": "lumo",
                    "style_text_key": "value_format",
                    "style_color_key": "value_color",
                    "style_size_key": "value_fontsize",
                }))
            elif label_id.startswith("gap_"):
                self._clickable_artists.append((artist, "text", {
                    "label_id": label_id,
                    "style_section": "gap_arrow",
                    "style_text_key": "format",
                    "style_color_key": "color",
                    "style_size_key": "fontsize",
                }))

        for homo_line in result.get("homo_lines", []):
            self._clickable_artists.append((homo_line, "line", {
                "style_section": "homo",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
            }))
        for lumo_line in result.get("lumo_lines", []):
            self._clickable_artists.append((lumo_line, "line", {
                "style_section": "lumo",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
            }))
        for arrow in result.get("arrows", []):
            self._clickable_artists.append((arrow, "arrow", {
                "style_section": "gap_arrow",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
            }))
