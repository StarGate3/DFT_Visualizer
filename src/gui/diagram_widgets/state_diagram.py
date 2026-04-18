"""S0/S1/T1 state energy diagram widget."""
from __future__ import annotations
import copy
import logging
from typing import Optional
from PyQt6.QtWidgets import QWidget
from src.data.models import DFTDataset
from src.gui.diagram_widgets.base_diagram import BaseDiagramWidget
from src.gui.diagram_widgets.draggable import DraggableArrowManager
from src.plotting.state_plot import StateDiagramPlotter
from src.plotting.style_presets import DEFAULT_STYLE, DiagramStyle

logger = logging.getLogger(__name__)


class StateDiagramWidget(BaseDiagramWidget):
    """Embeds a S0/S1/T1 state energy level diagram in the main tab area."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._plotter = StateDiagramPlotter()
        self._arrow_drag_manager: Optional[DraggableArrowManager] = None
        self._drag_base_offsets: dict = {}

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
        compounds = self._dataset.states
        logger.debug("StateDiagramWidget._draw: %d compounds", len(compounds))

        fig_s = self._style.get("figure", {})
        if "figsize" in fig_s:
            self.figure.set_size_inches(*fig_s["figsize"])

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        self._plotter.update_style(self._style)
        result = self._plotter.plot(ax, compounds, self._style)

        # Register draggable label artists
        self._setup_drag_manager(result.get("by_id", {}))

        # Set up arrow drag manager (horizontal-only drag for Abs./ISC arrows)
        arrow_artists = result.get("arrow_artists", {})
        if self._arrow_drag_manager is None:
            self._arrow_drag_manager = DraggableArrowManager(
                self.canvas,
                self._on_arrow_drag_start,
                self._on_arrow_dragged,
                self._on_arrow_drag_ended,
            )
        if not self._arrow_drag_manager.is_dragging:
            self._arrow_drag_manager.update_artists(arrow_artists)

        # Build clickable artist list for right-click context menus
        self._build_clickable_artists(result, compounds)

        self.canvas.draw_idle()

    def _build_clickable_artists(self, result: dict, compounds: list) -> None:
        self._clickable_artists = []
        by_id = result.get("by_id", {})

        for label_id, artist in by_id.items():
            matched = False
            for level in ("s0", "s1", "t1"):
                if label_id.startswith(f"{level}_value_"):
                    self._clickable_artists.append((artist, "text", {
                        "label_id": label_id,
                        "style_section": level,
                        "style_text_key": "value_format",
                        "style_color_key": "value_color",
                        "style_size_key": "value_fontsize",
                    }))
                    matched = True
                    break
                elif label_id.startswith(f"{level}_label_"):
                    self._clickable_artists.append((artist, "text", {
                        "label_id": label_id,
                        "style_section": level,
                        "style_text_key": "label_text",
                        "style_color_key": "label_color",
                        "style_size_key": "label_fontsize",
                    }))
                    matched = True
                    break
            if not matched:
                if label_id.startswith("abs_label_"):
                    self._clickable_artists.append((artist, "text", {
                        "label_id": label_id,
                        "style_section": "absorption_arrow",
                        "style_text_key": "label_text",
                        "style_color_key": "label_color",
                        "style_size_key": "label_fontsize",
                    }))
                elif label_id.startswith("isc_label_"):
                    self._clickable_artists.append((artist, "text", {
                        "label_id": label_id,
                        "style_section": "isc_curve",
                        "style_text_key": "label_text",
                        "style_color_key": "label_color",
                        "style_size_key": "label_fontsize",
                    }))

        for lines_key, section in (
            ("s0_lines", "s0"),
            ("s1_lines", "s1"),
            ("t1_lines", "t1"),
        ):
            for line in result.get(lines_key, []):
                self._clickable_artists.append((line, "line", {
                    "style_section": section,
                    "style_color_key": "color",
                    "style_lw_key": "linewidth",
                }))

        for arrow in result.get("abs_arrows", []):
            self._clickable_artists.append((arrow, "arrow", {
                "style_section": "absorption_arrow",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
            }))

        for patch in result.get("isc_curves", []):
            self._clickable_artists.append((patch, "arrow", {
                "style_section": "isc_curve",
                "style_color_key": "color",
                "style_lw_key": "linewidth",
                "style_show_key": "show",
            }))

    # ------------------------------------------------------------------
    # Arrow drag callbacks (horizontal repositioning via x_offset)
    # ------------------------------------------------------------------

    def _on_arrow_drag_start(self, arrow_type: str) -> None:
        style_key = "absorption_arrow" if arrow_type == "absorption" else "isc_curve"
        current_offset = self._style.get(style_key, {}).get("x_offset", 0.0)
        self._drag_base_offsets[arrow_type] = current_offset

    def _on_arrow_dragged(self, arrow_type: str, delta_x: float) -> None:
        style_key = "absorption_arrow" if arrow_type == "absorption" else "isc_curve"
        base = self._drag_base_offsets.get(arrow_type, 0.0)
        new_offset = round(base + delta_x, 3)
        self._style.setdefault(style_key, {})["x_offset"] = new_offset
        self._draw()

    def _on_arrow_drag_ended(self, arrow_type: str, delta_x: float) -> None:
        style_key = "absorption_arrow" if arrow_type == "absorption" else "isc_curve"
        base = self._drag_base_offsets.pop(arrow_type, 0.0)
        new_offset = round(base + delta_x, 3)
        self._style.setdefault(style_key, {})["x_offset"] = new_offset
        self._draw()
        self.style_changed.emit(copy.deepcopy(self._style))
