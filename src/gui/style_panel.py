"""Style and appearance panel for DFT Visualizer."""

from __future__ import annotations

import copy
import json
import logging
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QToolBox,
    QVBoxLayout,
    QWidget,
)

from matplotlib import font_manager as _mpl_fm

from src.plotting.style_presets import DEFAULT_STYLE, DiagramStyle, get_preset, list_presets

logger = logging.getLogger(__name__)

_SWATCH_SIZE = 16
_DEBOUNCE_MS = 200

# Publication-safe fonts that are reliably available across platforms and
# resolvable by matplotlib's font manager.
_PUBLICATION_FONTS: list[str] = [
    "Arial",
    "Helvetica",
    "Times New Roman",
    "DejaVu Sans",
    "DejaVu Serif",
    "Liberation Sans",
    "Liberation Serif",
    "Computer Modern Roman",
    "sans-serif",
    "serif",
    "monospace",
]

_FALLBACK_FONT = "DejaVu Sans"


def _is_font_available(name: str) -> bool:
    """Return True if matplotlib can resolve *name* without falling back."""
    try:
        _mpl_fm.findfont(name, fallback_to_default=False)
        return True
    except Exception:
        return False


class StylePanel(QWidget):
    """Right-dock panel for customising diagram appearance.

    Emits :attr:`style_changed` (with the full style dict) after a 200 ms
    debounce so rapid spinbox changes don't trigger a redraw on every tick.

    Signals:
        style_changed: Emitted with the current style dict after any control
            change, subject to a 200 ms debounce.
    """

    style_changed = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._updating: bool = False
        self._current_style: DiagramStyle = copy.deepcopy(DEFAULT_STYLE)
        self._setup_ui()
        self._init_debounce()
        # Populate controls with DEFAULT_STYLE values
        self.set_style(self._current_style)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner_widget = QWidget()
        self._inner_layout = QVBoxLayout(inner_widget)
        self._inner_layout.setContentsMargins(6, 6, 6, 6)
        self._inner_layout.setSpacing(6)

        self._build_preset_bar()
        self._build_separator()
        self._build_toolbox()
        self._build_bottom_buttons()
        self._inner_layout.addStretch()

        scroll.setWidget(inner_widget)
        outer.addWidget(scroll)

    def _build_preset_bar(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(4)

        self._preset_combo = QComboBox()
        self._preset_combo.addItems(list_presets())
        row.addWidget(QLabel("Preset:"))
        row.addWidget(self._preset_combo, 1)

        apply_btn = QPushButton("Apply")
        apply_btn.setFixedWidth(52)
        apply_btn.clicked.connect(self._apply_preset)
        row.addWidget(apply_btn)

        self._inner_layout.addLayout(row)

    def _build_separator(self) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self._inner_layout.addWidget(line)

    def _build_toolbox(self) -> None:
        # TODO (Stage 4+): hide/show sections based on the active diagram tab.
        self._toolbox = QToolBox()
        self._toolbox.addItem(self._build_general_section(), "General")
        self._toolbox.addItem(self._build_homo_section(), "HOMO")
        self._toolbox.addItem(self._build_lumo_section(), "LUMO")
        self._toolbox.addItem(self._build_gap_section(), "Gap Arrow")
        self._inner_layout.addWidget(self._toolbox)

    def _build_general_section(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(4, 4, 4, 4)
        form.setSpacing(6)

        _font_tooltip = (
            "Publication-safe fonts only. "
            "For LaTeX-style output, choose Computer Modern Roman."
        )
        self._font_combo = QComboBox()
        self._font_combo.addItems(_PUBLICATION_FONTS)
        self._font_combo.setToolTip(_font_tooltip)
        self._font_combo.currentTextChanged.connect(self._on_font_changed)
        # Set tooltip on the label too so hovering either widget shows it.
        font_label = QLabel("Font family:")
        font_label.setToolTip(_font_tooltip)
        form.addRow(font_label, self._font_combo)

        self._title_size_spin = QSpinBox()
        self._title_size_spin.setRange(8, 24)
        self._title_size_spin.valueChanged.connect(self._on_title_size_changed)
        form.addRow("Title size:", self._title_size_spin)

        self._title_text_edit = QLineEdit()
        self._title_text_edit.textChanged.connect(self._on_title_text_changed)
        form.addRow("Title text:", self._title_text_edit)

        self._ylabel_edit = QLineEdit()
        self._ylabel_edit.textChanged.connect(self._on_ylabel_changed)
        form.addRow("Y-axis label:", self._ylabel_edit)

        self._show_legend_cb = QCheckBox()
        self._show_legend_cb.stateChanged.connect(self._on_legend_changed)
        form.addRow("Show legend:", self._show_legend_cb)

        self._show_grid_cb = QCheckBox()
        self._show_grid_cb.stateChanged.connect(self._on_grid_changed)
        form.addRow("Show grid:", self._show_grid_cb)

        self._spine_lw_spin = QDoubleSpinBox()
        self._spine_lw_spin.setRange(0.5, 3.0)
        self._spine_lw_spin.setSingleStep(0.1)
        self._spine_lw_spin.setDecimals(1)
        self._spine_lw_spin.valueChanged.connect(self._on_spine_lw_changed)
        form.addRow("Spine width:", self._spine_lw_spin)

        self._bg_color_btn = QPushButton("Background color…")
        self._bg_color_btn.clicked.connect(lambda: self._pick_color("bg"))
        form.addRow("", self._bg_color_btn)

        return w

    def _build_homo_section(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(4, 4, 4, 4)
        form.setSpacing(6)

        self._homo_color_btn = QPushButton("HOMO color…")
        self._homo_color_btn.clicked.connect(lambda: self._pick_color("homo"))
        form.addRow("", self._homo_color_btn)

        self._homo_lw_spin = QDoubleSpinBox()
        self._homo_lw_spin.setRange(0.5, 5.0)
        self._homo_lw_spin.setSingleStep(0.25)
        self._homo_lw_spin.setDecimals(2)
        self._homo_lw_spin.valueChanged.connect(self._on_homo_lw_changed)
        form.addRow("Line width:", self._homo_lw_spin)

        self._homo_fs_spin = QSpinBox()
        self._homo_fs_spin.setRange(6, 16)
        self._homo_fs_spin.valueChanged.connect(self._on_homo_fs_changed)
        form.addRow("Value font size:", self._homo_fs_spin)

        self._homo_fmt_edit = QLineEdit()
        self._homo_fmt_edit.textChanged.connect(self._on_homo_fmt_changed)
        form.addRow("Value format:", self._homo_fmt_edit)

        self._homo_offset_spin = QSpinBox()
        self._homo_offset_spin.setRange(-30, 30)
        self._homo_offset_spin.setSingleStep(1)
        self._homo_offset_spin.setSuffix(" pt")
        self._homo_offset_spin.setToolTip(
            "Distance of value label from HOMO line in typographic points. "
            "Negative = below line, positive = above."
        )
        self._homo_offset_spin.valueChanged.connect(self._on_homo_offset_changed)
        form.addRow("Label offset:", self._homo_offset_spin)

        return w

    def _build_lumo_section(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(4, 4, 4, 4)
        form.setSpacing(6)

        self._lumo_color_btn = QPushButton("LUMO color…")
        self._lumo_color_btn.clicked.connect(lambda: self._pick_color("lumo"))
        form.addRow("", self._lumo_color_btn)

        self._lumo_lw_spin = QDoubleSpinBox()
        self._lumo_lw_spin.setRange(0.5, 5.0)
        self._lumo_lw_spin.setSingleStep(0.25)
        self._lumo_lw_spin.setDecimals(2)
        self._lumo_lw_spin.valueChanged.connect(self._on_lumo_lw_changed)
        form.addRow("Line width:", self._lumo_lw_spin)

        self._lumo_fs_spin = QSpinBox()
        self._lumo_fs_spin.setRange(6, 16)
        self._lumo_fs_spin.valueChanged.connect(self._on_lumo_fs_changed)
        form.addRow("Value font size:", self._lumo_fs_spin)

        self._lumo_fmt_edit = QLineEdit()
        self._lumo_fmt_edit.textChanged.connect(self._on_lumo_fmt_changed)
        form.addRow("Value format:", self._lumo_fmt_edit)

        self._lumo_offset_spin = QSpinBox()
        self._lumo_offset_spin.setRange(-30, 30)
        self._lumo_offset_spin.setSingleStep(1)
        self._lumo_offset_spin.setSuffix(" pt")
        self._lumo_offset_spin.setToolTip(
            "Distance of value label from LUMO line in typographic points. "
            "Negative = below line, positive = above."
        )
        self._lumo_offset_spin.valueChanged.connect(self._on_lumo_offset_changed)
        form.addRow("Label offset:", self._lumo_offset_spin)

        return w

    def _build_gap_section(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(4, 4, 4, 4)
        form.setSpacing(6)

        self._arrow_color_btn = QPushButton("Arrow color…")
        self._arrow_color_btn.clicked.connect(lambda: self._pick_color("arrow"))
        form.addRow("", self._arrow_color_btn)

        self._arrow_lw_spin = QDoubleSpinBox()
        self._arrow_lw_spin.setRange(0.25, 5.0)
        self._arrow_lw_spin.setSingleStep(0.25)
        self._arrow_lw_spin.setDecimals(2)
        self._arrow_lw_spin.valueChanged.connect(self._on_arrow_lw_changed)
        form.addRow("Arrow width:", self._arrow_lw_spin)

        self._gap_fs_spin = QSpinBox()
        self._gap_fs_spin.setRange(6, 16)
        self._gap_fs_spin.valueChanged.connect(self._on_gap_fs_changed)
        form.addRow("Gap font size:", self._gap_fs_spin)

        self._gap_fmt_edit = QLineEdit()
        self._gap_fmt_edit.textChanged.connect(self._on_gap_fmt_changed)
        form.addRow("Gap format:", self._gap_fmt_edit)

        return w

    def _build_bottom_buttons(self) -> None:
        for label, slot in [
            ("Reset to Default", self._reset_to_default),
            ("Export Style as JSON…", self._export_style),
            ("Import Style from JSON…", self._import_style),
        ]:
            btn = QPushButton(label)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(slot)
            self._inner_layout.addWidget(btn)

    # ------------------------------------------------------------------
    # Debounce
    # ------------------------------------------------------------------

    def _init_debounce(self) -> None:
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(_DEBOUNCE_MS)
        self._debounce_timer.timeout.connect(self._emit_style_changed)

    def _schedule_emit(self) -> None:
        """Restart the debounce timer; emits style_changed after 200 ms idle."""
        self._debounce_timer.start()

    def _emit_style_changed(self) -> None:
        logger.debug("StylePanel emitting style_changed")
        self.style_changed.emit(copy.deepcopy(self._current_style))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_style(self) -> DiagramStyle:
        """Return a copy of the current style configuration.

        Returns:
            A deep copy of the internal style dict.
        """
        return copy.deepcopy(self._current_style)

    def set_style(self, style: DiagramStyle) -> None:
        """Update all controls to reflect *style* without emitting signals.

        Args:
            style: The style dict to apply.
        """
        self._updating = True
        try:
            self._current_style = copy.deepcopy(style)
            requested_font = style["title"]["fontfamily"]
            if requested_font not in _PUBLICATION_FONTS or not _is_font_available(requested_font):
                if requested_font not in _PUBLICATION_FONTS:
                    logger.warning(
                        "Font '%s' not in curated list; falling back to %s",
                        requested_font, _FALLBACK_FONT,
                    )
                self._current_style["title"]["fontfamily"] = _FALLBACK_FONT
                self._current_style["axes"]["label_fontfamily"] = _FALLBACK_FONT
                self._current_style["compound_labels"]["fontfamily"] = _FALLBACK_FONT
                requested_font = _FALLBACK_FONT
            self._font_combo.setCurrentText(requested_font)
            self._title_size_spin.setValue(style["title"]["fontsize"])
            self._title_text_edit.setText(style["title"]["text"])
            self._ylabel_edit.setText(style["axes"]["ylabel"])
            self._show_legend_cb.setChecked(style["legend"]["visible"])
            self._show_grid_cb.setChecked(style["axes"]["show_grid"])
            self._spine_lw_spin.setValue(style["axes"]["spine_linewidth"])
            self._set_color_btn(self._bg_color_btn, style["figure"]["background_color"])

            self._set_color_btn(self._homo_color_btn, style["homo"]["color"])
            self._homo_lw_spin.setValue(style["homo"]["linewidth"])
            self._homo_fs_spin.setValue(style["homo"]["value_fontsize"])
            self._homo_fmt_edit.setText(style["homo"]["value_format"])
            self._homo_offset_spin.setValue(style["homo"].get("value_offset_points", -8))

            self._set_color_btn(self._lumo_color_btn, style["lumo"]["color"])
            self._lumo_lw_spin.setValue(style["lumo"]["linewidth"])
            self._lumo_fs_spin.setValue(style["lumo"]["value_fontsize"])
            self._lumo_fmt_edit.setText(style["lumo"]["value_format"])
            self._lumo_offset_spin.setValue(style["lumo"].get("value_offset_points", 8))

            self._set_color_btn(self._arrow_color_btn, style["gap_arrow"]["color"])
            self._arrow_lw_spin.setValue(style["gap_arrow"]["linewidth"])
            self._gap_fs_spin.setValue(style["gap_arrow"]["fontsize"])
            self._gap_fmt_edit.setText(style["gap_arrow"]["format"])
        finally:
            self._updating = False

    # ------------------------------------------------------------------
    # Control → style dict update slots
    # ------------------------------------------------------------------

    def _on_font_changed(self, family: str) -> None:
        if self._updating:
            return
        self._current_style["title"]["fontfamily"] = family
        self._current_style["axes"]["label_fontfamily"] = family
        self._current_style["compound_labels"]["fontfamily"] = family
        self._schedule_emit()

    def _on_title_size_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["title"]["fontsize"] = value
        self._schedule_emit()

    def _on_title_text_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["title"]["text"] = text
        self._schedule_emit()

    def _on_ylabel_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["axes"]["ylabel"] = text
        self._schedule_emit()

    def _on_legend_changed(self, _: int) -> None:
        if self._updating:
            return
        self._current_style["legend"]["visible"] = self._show_legend_cb.isChecked()
        self._schedule_emit()

    def _on_grid_changed(self, _: int) -> None:
        if self._updating:
            return
        self._current_style["axes"]["show_grid"] = self._show_grid_cb.isChecked()
        self._schedule_emit()

    def _on_spine_lw_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["axes"]["spine_linewidth"] = value
        self._schedule_emit()

    def _on_homo_lw_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["homo"]["linewidth"] = value
        self._schedule_emit()

    def _on_homo_fs_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["homo"]["value_fontsize"] = value
        self._schedule_emit()

    def _on_homo_fmt_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["homo"]["value_format"] = text
        self._schedule_emit()

    def _on_lumo_lw_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["lumo"]["linewidth"] = value
        self._schedule_emit()

    def _on_lumo_fs_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["lumo"]["value_fontsize"] = value
        self._schedule_emit()

    def _on_lumo_fmt_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["lumo"]["value_format"] = text
        self._schedule_emit()

    def _on_homo_offset_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["homo"]["value_offset_points"] = value
        self._schedule_emit()

    def _on_lumo_offset_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["lumo"]["value_offset_points"] = value
        self._schedule_emit()

    def _on_arrow_lw_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["gap_arrow"]["linewidth"] = value
        self._schedule_emit()

    def _on_gap_fs_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["gap_arrow"]["fontsize"] = value
        self._schedule_emit()

    def _on_gap_fmt_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["gap_arrow"]["format"] = text
        self._schedule_emit()

    # ------------------------------------------------------------------
    # Color picker helper
    # ------------------------------------------------------------------

    def _pick_color(self, target: str) -> None:
        """Open a color dialog and update the relevant style field."""
        color_map = {
            "bg":   ("figure", "background_color", self._bg_color_btn),
            "homo": ("homo",   "color",             self._homo_color_btn),
            "lumo": ("lumo",   "color",             self._lumo_color_btn),
            "arrow":("gap_arrow","color",            self._arrow_color_btn),
        }
        section, key, btn = color_map[target]
        current = self._current_style[section][key]  # type: ignore[index]
        initial = QColor(current)
        color = QColorDialog.getColor(initial, self, "Choose Color")
        if not color.isValid():
            return
        hex_color = color.name()
        self._current_style[section][key] = hex_color  # type: ignore[index]
        # HOMO value_color mirrors HOMO color for consistency
        if target == "homo":
            self._current_style["homo"]["value_color"] = hex_color
        elif target == "lumo":
            self._current_style["lumo"]["value_color"] = hex_color
        self._set_color_btn(btn, hex_color)
        self._schedule_emit()

    def _set_color_btn(self, btn: QPushButton, hex_color: str) -> None:
        """Update button icon to show a colored swatch."""
        pixmap = QPixmap(_SWATCH_SIZE, _SWATCH_SIZE)
        pixmap.fill(QColor(hex_color))
        btn.setIcon(QIcon(pixmap))

    # ------------------------------------------------------------------
    # Preset / bottom button handlers
    # ------------------------------------------------------------------

    def _apply_preset(self) -> None:
        name = self._preset_combo.currentText()
        try:
            style = get_preset(name)
        except KeyError:
            return
        self.set_style(style)
        self._emit_style_changed()

    def _reset_to_default(self) -> None:
        self.set_style(copy.deepcopy(DEFAULT_STYLE))
        self._emit_style_changed()

    def _export_style(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Style", "", "JSON Files (*.json)"
        )
        if not filepath:
            return
        style = self.get_style()
        # Convert tuple to list for JSON serialisation
        style["figure"]["figsize"] = list(style["figure"]["figsize"])  # type: ignore[assignment]
        try:
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(style, fh, indent=2)
        except OSError as exc:
            QMessageBox.critical(self, "Export Error", str(exc))

    def _import_style(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Style", "", "JSON Files (*.json)"
        )
        if not filepath:
            return
        try:
            with open(filepath, encoding="utf-8") as fh:
                style = json.load(fh)
            # Restore figsize tuple
            if "figure" in style and "figsize" in style["figure"]:
                style["figure"]["figsize"] = tuple(style["figure"]["figsize"])
            self.set_style(style)
            self._emit_style_changed()
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            QMessageBox.critical(self, "Import Error", f"Could not load style: {exc}")
