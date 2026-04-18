"""Abstract base class for all diagram widgets."""

from __future__ import annotations

import copy
import logging
from abc import abstractmethod
from pathlib import Path
from typing import Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtWidgets import (
    QColorDialog,
    QDoubleSpinBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QInputDialog,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from src.data.models import DFTDataset
from src.gui.diagram_widgets.draggable import DraggableTextManager

logger = logging.getLogger(__name__)


class BaseDiagramWidget(QWidget):
    """Base class for HOMO/LUMO, States, and Franck-Condon diagram widgets.

    Owns the matplotlib Figure + FigureCanvasQTAgg and the navigation toolbar.
    Subclasses implement :meth:`refresh` to render their specific diagram type.

    Signals:
        style_changed: Emitted when the user modifies a label (drag or
            right-click context menu action) with the updated style dict.
    """

    style_changed = pyqtSignal(dict)

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

        # Shared state for drag and context menus
        self._dataset: Optional[DFTDataset] = None
        self._style: Optional[dict] = None
        self._drag_manager: Optional[DraggableTextManager] = None
        # list of (artist, type_str, metadata_dict)
        self._clickable_artists: list = []

        self._right_click_cid = self.canvas.mpl_connect(
            "button_press_event", self._on_canvas_right_click
        )

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def refresh(self, dataset: DFTDataset, style: dict) -> None:
        """Re-render the diagram using *dataset* and *style*."""

    # ------------------------------------------------------------------
    # Drag manager helpers
    # ------------------------------------------------------------------

    def _setup_drag_manager(self, artists_by_id: dict) -> None:
        """Register draggable text artists from the plotter's by_id dict."""
        if self._drag_manager is None:
            self._drag_manager = DraggableTextManager(
                self.canvas, self._on_label_moved
            )
        else:
            self._drag_manager.clear()
        for label_id, artist in artists_by_id.items():
            self._drag_manager.register(artist, label_id)

    def _on_label_moved(
        self, label_id: str, new_xy: tuple[float, float]
    ) -> None:
        if self._style is None:
            return
        overrides = self._style.setdefault("label_overrides", {})
        overrides[label_id] = list(new_xy)
        self.style_changed.emit(copy.deepcopy(self._style))

    # ------------------------------------------------------------------
    # Right-click context menus
    # ------------------------------------------------------------------

    def _on_canvas_right_click(self, event) -> None:
        if event.button != 3:
            return
        for artist, artist_type, metadata in self._clickable_artists:
            try:
                contains, _ = artist.contains(event)
            except Exception:
                continue
            if contains:
                self._show_artist_menu(artist, artist_type, metadata)
                return
        self._show_empty_menu()

    def _show_artist_menu(
        self, artist, artist_type: str, metadata: dict
    ) -> None:
        menu = QMenu(self)
        actions: dict[str, object] = {}

        if artist_type == "text":
            actions["edit"] = menu.addAction("Edit text\u2026")
            actions["color"] = menu.addAction("Change color\u2026")
            actions["size"] = menu.addAction("Change font size\u2026")
            label_id = metadata.get("label_id")
            if label_id:
                menu.addSeparator()
                actions["reset_pos"] = menu.addAction("Reset position")
        elif artist_type == "line":
            actions["color"] = menu.addAction("Change color\u2026")
            actions["lw"] = menu.addAction("Change line width\u2026")
            actions["ls"] = menu.addAction("Change line style\u2026")
        elif artist_type == "arrow":
            actions["color"] = menu.addAction("Change color\u2026")
            actions["lw"] = menu.addAction("Change line width\u2026")
            show_key = metadata.get("style_show_key")
            if show_key:
                section = metadata.get("style_section", "")
                is_visible = self._style.get(section, {}).get(show_key, True) if self._style else True
                label = "Hide" if is_visible else "Show"
                actions["toggle"] = menu.addAction(label)
        else:
            return

        chosen = menu.exec(QCursor.pos())
        if chosen is None:
            return

        if chosen == actions.get("edit"):
            self._ctx_edit_text(artist, metadata)
        elif chosen == actions.get("color"):
            self._ctx_change_color(artist, metadata)
        elif chosen == actions.get("size"):
            self._ctx_change_fontsize(artist, metadata)
        elif chosen == actions.get("reset_pos"):
            self._ctx_reset_position(metadata.get("label_id", ""))
        elif chosen == actions.get("lw"):
            self._ctx_change_linewidth(artist, metadata)
        elif chosen == actions.get("ls"):
            self._ctx_change_linestyle(artist, metadata)
        elif chosen == actions.get("toggle"):
            self._ctx_toggle_visibility(artist, metadata)

    def _show_empty_menu(self) -> None:
        menu = QMenu(self)
        reset_all = menu.addAction("Reset all label positions")
        menu.addSeparator()
        quick_save = menu.addAction("Save as PNG\u2026")

        chosen = menu.exec(QCursor.pos())
        if chosen == reset_all:
            if self._style is not None:
                self._style.pop("label_overrides", None)
                if self._dataset is not None:
                    self.refresh(self._dataset, self._style)
                self.style_changed.emit(copy.deepcopy(self._style))
        elif chosen == quick_save:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save as PNG", "", "PNG Files (*.png)"
            )
            if filepath:
                p = Path(filepath)
                if p.suffix.lower() != ".png":
                    p = p.with_suffix(".png")
                self.export_figure(p, dpi=150, fmt="png", figsize_cm=None, background="white")

    # ------------------------------------------------------------------
    # Context menu actions
    # ------------------------------------------------------------------

    def _ctx_edit_text(self, artist, metadata: dict) -> None:
        section = metadata.get("style_section", "")
        text_key = metadata.get("style_text_key", "label_text")
        if self._style and section and text_key:
            current = self._style.get(section, {}).get(text_key, artist.get_text())
        else:
            current = artist.get_text()
        new_text, ok = QInputDialog.getText(
            self, "Edit Text", "Text:", text=current
        )
        if not ok:
            return
        if self._style and section and text_key:
            self._style.setdefault(section, {})[text_key] = new_text
        artist.set_text(new_text)
        self.canvas.draw_idle()
        if self._style is not None:
            self.style_changed.emit(copy.deepcopy(self._style))

    def _ctx_change_color(self, artist, metadata: dict) -> None:
        section = metadata.get("style_section", "")
        color_key = metadata.get("style_color_key", "color")
        try:
            current_hex = self._style.get(section, {}).get(color_key, "#000000") if self._style else "#000000"
        except Exception:
            current_hex = "#000000"
        color = QColorDialog.getColor(QColor(current_hex), self, "Choose Color")
        if not color.isValid():
            return
        new_hex = color.name()
        if self._style and section and color_key:
            self._style.setdefault(section, {})[color_key] = new_hex
        try:
            artist.set_color(new_hex)
        except Exception as exc:
            logger.debug("set_color failed: %s", exc)
        self.canvas.draw_idle()
        if self._style is not None:
            self.style_changed.emit(copy.deepcopy(self._style))

    def _ctx_change_fontsize(self, artist, metadata: dict) -> None:
        try:
            current = int(artist.get_fontsize())
        except Exception:
            current = 11
        new_size, ok = QInputDialog.getInt(
            self, "Font Size", "Size (pt):", current, 6, 72
        )
        if not ok:
            return
        section = metadata.get("style_section", "")
        size_key = metadata.get("style_size_key", "label_fontsize")
        if self._style and section and size_key:
            self._style.setdefault(section, {})[size_key] = new_size
        artist.set_fontsize(new_size)
        self.canvas.draw_idle()
        if self._style is not None:
            self.style_changed.emit(copy.deepcopy(self._style))

    def _ctx_reset_position(self, label_id: str) -> None:
        if not label_id or self._style is None:
            return
        self._style.get("label_overrides", {}).pop(label_id, None)
        if self._dataset is not None:
            self.refresh(self._dataset, self._style)
        self.style_changed.emit(copy.deepcopy(self._style))

    def _ctx_change_linewidth(self, artist, metadata: dict) -> None:
        try:
            current = float(artist.get_linewidth())
        except Exception:
            current = 1.5
        new_lw, ok = QInputDialog.getDouble(
            self, "Line Width", "Width:", current, 0.1, 10.0, 1
        )
        if not ok:
            return
        section = metadata.get("style_section", "")
        lw_key = metadata.get("style_lw_key", "linewidth")
        if self._style and section and lw_key:
            self._style.setdefault(section, {})[lw_key] = new_lw
        try:
            artist.set_linewidth(new_lw)
        except Exception as exc:
            logger.debug("set_linewidth failed: %s", exc)
        self.canvas.draw_idle()
        if self._style is not None:
            self.style_changed.emit(copy.deepcopy(self._style))

    def _ctx_change_linestyle(self, artist, metadata: dict) -> None:
        ls_names = ["solid", "dashed", "dotted", "dashdot"]
        choice, ok = QInputDialog.getItem(
            self, "Line Style", "Style:", ls_names, 0, False
        )
        if not ok:
            return
        ls_map = {"solid": "-", "dashed": "--", "dotted": ":", "dashdot": "-."}
        section = metadata.get("style_section", "")
        ls_key = metadata.get("style_ls_key", "linestyle")
        if self._style and section:
            self._style.setdefault(section, {})[ls_key] = choice
        try:
            artist.set_linestyle(ls_map.get(choice, "-"))
        except Exception as exc:
            logger.debug("set_linestyle failed: %s", exc)
        self.canvas.draw_idle()
        if self._style is not None:
            self.style_changed.emit(copy.deepcopy(self._style))

    def _ctx_toggle_visibility(self, artist, metadata: dict) -> None:
        section = metadata.get("style_section", "")
        show_key = metadata.get("style_show_key", "show")
        if self._style and section and show_key:
            current = self._style.get(section, {}).get(show_key, True)
            new_val = not current
            self._style.setdefault(section, {})[show_key] = new_val
            try:
                artist.set_visible(new_val)
            except Exception as exc:
                logger.debug("set_visible failed: %s", exc)
            self.canvas.draw_idle()
            self.style_changed.emit(copy.deepcopy(self._style))

    # ------------------------------------------------------------------
    # Export
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
        """Save the figure to *filepath* with publication-quality settings."""
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
