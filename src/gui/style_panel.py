"""Style and appearance panel for DFT Visualizer.

This implementation uses THREE separate QToolBox instances inside a
QStackedWidget — one per diagram tab. Each toolbox owns its own page
widgets; nothing is shared between toolboxes, so there is no widget
reparenting during tab switches. Tab switching is a simple
``QStackedWidget.setCurrentIndex`` call.

The General section appears in all three toolboxes with independent
widget copies. The copies are kept synchronised via the shared
``self._current_style`` dict and ``_sync_general_control``.
"""

from __future__ import annotations

import copy
import json
import logging
from typing import Optional

from PyQt6.QtCore import QTimer, pyqtSignal
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
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QToolBox,
    QVBoxLayout,
    QWidget,
)

from matplotlib import font_manager as _mpl_fm

from src.plotting.style_presets import DEFAULT_STYLE, DiagramStyle, get_preset, list_presets

logger = logging.getLogger(__name__)

_SWATCH_SIZE = 16
_DEBOUNCE_MS = 200

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

    Uses a QStackedWidget containing three independent QToolBox widgets,
    one for each diagram tab. Tab switching is a no-cost index change.

    Signals:
        style_changed: Emitted with the current style dict after any control
            change, subject to a 200 ms debounce.
    """

    style_changed = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._updating: bool = False
        self._current_style: DiagramStyle = copy.deepcopy(DEFAULT_STYLE)

        # Storage for control widget references, keyed by scope where needed.
        self._general_controls: dict[str, dict] = {}
        self._state_controls: dict[str, dict] = {}

        self._setup_ui()
        self._init_debounce()
        self.set_style(self._current_style)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(4)

        self._build_preset_bar(outer)
        self._add_separator(outer)

        self._stack = QStackedWidget(self)
        self._stack.addWidget(self._build_toolbox_for_homo_lumo())       # index 0
        self._stack.addWidget(self._build_toolbox_for_states())          # index 1
        self._stack.addWidget(self._build_toolbox_for_franck_condon())   # index 2
        outer.addWidget(self._stack, 1)

        self._build_bottom_buttons(outer)

    def _build_preset_bar(self, layout: QVBoxLayout) -> None:
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

        layout.addLayout(row)

    def _add_separator(self, layout: QVBoxLayout) -> None:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

    def _build_toolbox_for_homo_lumo(self) -> QToolBox:
        tb = QToolBox()
        tb.addItem(self._build_general_page("hl"), "General")
        tb.addItem(self._build_homo_page(), "HOMO")
        tb.addItem(self._build_lumo_page(), "LUMO")
        tb.addItem(self._build_gap_page(), "Gap Arrow")
        return tb

    def _build_toolbox_for_states(self) -> QToolBox:
        tb = QToolBox()
        tb.addItem(self._build_general_page("st"), "General")
        tb.addItem(self._build_state_level_page("s0", "S0"), "S0")
        tb.addItem(self._build_state_level_page("s1", "S1"), "S1")
        tb.addItem(self._build_state_level_page("t1", "T1"), "T1")
        tb.addItem(self._build_abs_page(), "Absorption Arrow")
        tb.addItem(self._build_isc_page(), "ISC Curve")
        return tb

    def _build_toolbox_for_franck_condon(self) -> QToolBox:
        tb = QToolBox()
        tb.addItem(self._build_general_page("fc"), "General")
        return tb

    def _make_page(self) -> tuple[QWidget, QFormLayout]:
        w = QWidget()
        form = QFormLayout(w)
        form.setContentsMargins(6, 6, 6, 6)
        form.setSpacing(6)
        return w, form

    # ------------------------------------------------------------------
    # General page (one copy per scope: "hl", "st", "fc")
    # ------------------------------------------------------------------

    def _build_general_page(self, scope: str) -> QWidget:
        w, form = self._make_page()
        controls: dict = {}

        font_tooltip = (
            "Publication-safe fonts only. "
            "For LaTeX-style output, choose Computer Modern Roman."
        )

        font_combo = QComboBox()
        font_combo.addItems(_PUBLICATION_FONTS)
        font_combo.setToolTip(font_tooltip)
        font_combo.currentTextChanged.connect(self._on_font_changed)
        font_label = QLabel("Font family:")
        font_label.setToolTip(font_tooltip)
        form.addRow(font_label, font_combo)
        controls["font_combo"] = font_combo

        title_size_spin = QSpinBox()
        title_size_spin.setRange(8, 24)
        title_size_spin.valueChanged.connect(self._on_title_size_changed)
        form.addRow("Title size:", title_size_spin)
        controls["title_size_spin"] = title_size_spin

        title_text_edit = QLineEdit()
        title_text_edit.textChanged.connect(self._on_title_text_changed)
        form.addRow("Title text:", title_text_edit)
        controls["title_text_edit"] = title_text_edit

        ylabel_edit = QLineEdit()
        ylabel_edit.textChanged.connect(self._on_ylabel_changed)
        form.addRow("Y-axis label:", ylabel_edit)
        controls["ylabel_edit"] = ylabel_edit

        show_legend_cb = QCheckBox()
        show_legend_cb.stateChanged.connect(self._on_legend_changed)
        form.addRow("Show legend:", show_legend_cb)
        controls["show_legend_cb"] = show_legend_cb

        show_grid_cb = QCheckBox()
        show_grid_cb.stateChanged.connect(self._on_grid_changed)
        form.addRow("Show grid:", show_grid_cb)
        controls["show_grid_cb"] = show_grid_cb

        spine_lw_spin = QDoubleSpinBox()
        spine_lw_spin.setRange(0.5, 3.0)
        spine_lw_spin.setSingleStep(0.1)
        spine_lw_spin.setDecimals(1)
        spine_lw_spin.valueChanged.connect(self._on_spine_lw_changed)
        form.addRow("Spine width:", spine_lw_spin)
        controls["spine_lw_spin"] = spine_lw_spin

        bg_color_btn = QPushButton("Background color…")
        bg_color_btn.clicked.connect(lambda: self._pick_color("bg"))
        form.addRow("", bg_color_btn)
        controls["bg_color_btn"] = bg_color_btn

        self._general_controls[scope] = controls
        return w

    def _sync_general_control(self, key: str, value, setter: str) -> None:
        """Propagate a General-section change to all other scopes silently."""
        self._updating = True
        try:
            for controls in self._general_controls.values():
                widget = controls.get(key)
                if widget is None:
                    continue
                widget.blockSignals(True)
                try:
                    getattr(widget, setter)(value)
                finally:
                    widget.blockSignals(False)
        finally:
            self._updating = False

    # ------------------------------------------------------------------
    # HOMO / LUMO / Gap pages (single instance each — appear only in HL toolbox)
    # ------------------------------------------------------------------

    def _build_homo_page(self) -> QWidget:
        w, form = self._make_page()

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

    def _build_lumo_page(self) -> QWidget:
        w, form = self._make_page()

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

    def _build_gap_page(self) -> QWidget:
        w, form = self._make_page()

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

    # ------------------------------------------------------------------
    # State level pages (S0, S1, T1)
    # ------------------------------------------------------------------

    def _build_state_level_page(self, level: str, title: str) -> QWidget:
        w, form = self._make_page()

        color_btn = QPushButton(f"{title} color…")
        color_btn.clicked.connect(lambda checked, lv=level: self._pick_color(lv))
        form.addRow("", color_btn)

        lw_spin = QDoubleSpinBox()
        lw_spin.setRange(0.5, 5.0)
        lw_spin.setSingleStep(0.25)
        lw_spin.setDecimals(2)
        lw_spin.valueChanged.connect(lambda v, lv=level: self._on_state_lw_changed(lv, v))
        form.addRow("Line width:", lw_spin)

        val_fs_spin = QSpinBox()
        val_fs_spin.setRange(6, 16)
        val_fs_spin.valueChanged.connect(lambda v, lv=level: self._on_state_val_fs_changed(lv, v))
        form.addRow("Value font size:", val_fs_spin)

        offset_spin = QSpinBox()
        offset_spin.setRange(-30, 30)
        offset_spin.setSingleStep(1)
        offset_spin.setSuffix(" pt")
        offset_spin.valueChanged.connect(lambda v, lv=level: self._on_state_offset_changed(lv, v))
        form.addRow("Label offset:", offset_spin)

        label_text_edit = QLineEdit()
        label_text_edit.textChanged.connect(
            lambda t, lv=level: self._on_state_label_text_changed(lv, t)
        )
        form.addRow("Label text:", label_text_edit)

        label_fs_spin = QSpinBox()
        label_fs_spin.setRange(6, 16)
        label_fs_spin.valueChanged.connect(
            lambda v, lv=level: self._on_state_label_fs_changed(lv, v)
        )
        form.addRow("Label font size:", label_fs_spin)

        self._state_controls[level] = {
            "color_btn": color_btn,
            "lw_spin": lw_spin,
            "val_fs_spin": val_fs_spin,
            "offset_spin": offset_spin,
            "label_text_edit": label_text_edit,
            "label_fs_spin": label_fs_spin,
        }

        return w

    def _build_abs_page(self) -> QWidget:
        w, form = self._make_page()

        self._abs_color_btn = QPushButton("Arrow color…")
        self._abs_color_btn.clicked.connect(lambda: self._pick_color("abs"))
        form.addRow("", self._abs_color_btn)

        self._abs_lw_spin = QDoubleSpinBox()
        self._abs_lw_spin.setRange(0.25, 5.0)
        self._abs_lw_spin.setSingleStep(0.25)
        self._abs_lw_spin.setDecimals(2)
        self._abs_lw_spin.valueChanged.connect(self._on_abs_lw_changed)
        form.addRow("Line width:", self._abs_lw_spin)

        self._abs_show_label_cb = QCheckBox()
        self._abs_show_label_cb.stateChanged.connect(self._on_abs_show_label_changed)
        form.addRow("Show label:", self._abs_show_label_cb)

        self._abs_label_edit = QLineEdit()
        self._abs_label_edit.textChanged.connect(self._on_abs_label_text_changed)
        form.addRow("Label text:", self._abs_label_edit)

        self._abs_label_fs_spin = QSpinBox()
        self._abs_label_fs_spin.setRange(6, 16)
        self._abs_label_fs_spin.valueChanged.connect(self._on_abs_label_fs_changed)
        form.addRow("Label font size:", self._abs_label_fs_spin)

        return w

    def _build_isc_page(self) -> QWidget:
        w, form = self._make_page()

        self._isc_color_btn = QPushButton("Curve color…")
        self._isc_color_btn.clicked.connect(lambda: self._pick_color("isc"))
        form.addRow("", self._isc_color_btn)

        self._isc_lw_spin = QDoubleSpinBox()
        self._isc_lw_spin.setRange(0.25, 5.0)
        self._isc_lw_spin.setSingleStep(0.25)
        self._isc_lw_spin.setDecimals(2)
        self._isc_lw_spin.valueChanged.connect(self._on_isc_lw_changed)
        form.addRow("Line width:", self._isc_lw_spin)

        self._isc_show_label_cb = QCheckBox()
        self._isc_show_label_cb.stateChanged.connect(self._on_isc_show_label_changed)
        form.addRow("Show label:", self._isc_show_label_cb)

        self._isc_label_edit = QLineEdit()
        self._isc_label_edit.textChanged.connect(self._on_isc_label_text_changed)
        form.addRow("Label text:", self._isc_label_edit)

        self._isc_label_fs_spin = QSpinBox()
        self._isc_label_fs_spin.setRange(6, 16)
        self._isc_label_fs_spin.valueChanged.connect(self._on_isc_label_fs_changed)
        form.addRow("Label font size:", self._isc_label_fs_spin)

        self._isc_curvature_spin = QDoubleSpinBox()
        self._isc_curvature_spin.setRange(0.0, 1.0)
        self._isc_curvature_spin.setSingleStep(0.05)
        self._isc_curvature_spin.setDecimals(2)
        self._isc_curvature_spin.setValue(0.3)
        self._isc_curvature_spin.valueChanged.connect(self._on_isc_curvature_changed)
        form.addRow("Curvature:", self._isc_curvature_spin)

        return w

    def _build_bottom_buttons(self, layout: QVBoxLayout) -> None:
        for label, slot in [
            ("Reset to Default", self._reset_to_default),
            ("Export Style as JSON…", self._export_style),
            ("Import Style from JSON…", self._import_style),
        ]:
            btn = QPushButton(label)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

    # ------------------------------------------------------------------
    # Tab switching — now trivial
    # ------------------------------------------------------------------

    def set_active_tab(self, idx: int) -> None:
        """Switch the visible QToolBox for *idx* via the inner QStackedWidget.

        No widget reparenting, no removeItem/addItem. This is a no-cost
        index change and cannot recurse.
        """
        if 0 <= idx < self._stack.count():
            self._stack.setCurrentIndex(idx)

    # ------------------------------------------------------------------
    # Debounce
    # ------------------------------------------------------------------

    def _init_debounce(self) -> None:
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(_DEBOUNCE_MS)
        self._debounce_timer.timeout.connect(self._emit_style_changed)

    def _schedule_emit(self) -> None:
        self._debounce_timer.start()

    def _emit_style_changed(self) -> None:
        self.style_changed.emit(copy.deepcopy(self._current_style))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_style(self) -> DiagramStyle:
        return copy.deepcopy(self._current_style)

    def set_style(self, style: DiagramStyle) -> None:
        """Update all controls from *style* without emitting signals."""
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

            # Apply to every General section scope
            for controls in self._general_controls.values():
                controls["font_combo"].setCurrentText(requested_font)
                controls["title_size_spin"].setValue(style["title"]["fontsize"])
                controls["title_text_edit"].setText(style["title"]["text"])
                controls["ylabel_edit"].setText(style["axes"]["ylabel"])
                controls["show_legend_cb"].setChecked(style["legend"]["visible"])
                controls["show_grid_cb"].setChecked(style["axes"]["show_grid"])
                controls["spine_lw_spin"].setValue(style["axes"]["spine_linewidth"])
                self._set_color_btn(
                    controls["bg_color_btn"], style["figure"]["background_color"]
                )

            # HOMO / LUMO / Gap (single instances)
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

            # State levels
            for level in ("s0", "s1", "t1"):
                level_s = style.get(level, {})  # type: ignore[call-overload]
                if not level_s:
                    continue
                ctrl = self._state_controls.get(level, {})
                if not ctrl:
                    continue
                self._set_color_btn(ctrl["color_btn"], level_s.get("color", "#000000"))
                ctrl["lw_spin"].setValue(level_s.get("linewidth", 2.0))
                ctrl["val_fs_spin"].setValue(level_s.get("value_fontsize", 9))
                ctrl["offset_spin"].setValue(level_s.get("value_offset_points", 10))
                ctrl["label_text_edit"].setText(level_s.get("label_text", level.upper()))
                ctrl["label_fs_spin"].setValue(level_s.get("label_fontsize", 10))

            abs_s = style.get("absorption_arrow", {})  # type: ignore[call-overload]
            if abs_s:
                self._set_color_btn(self._abs_color_btn, abs_s.get("color", "#333333"))
                self._abs_lw_spin.setValue(abs_s.get("linewidth", 1.5))
                self._abs_show_label_cb.setChecked(abs_s.get("show_label", True))
                self._abs_label_edit.setText(abs_s.get("label_text", "Abs."))
                self._abs_label_fs_spin.setValue(abs_s.get("label_fontsize", 9))

            isc_s = style.get("isc_curve", {})  # type: ignore[call-overload]
            if isc_s:
                self._set_color_btn(self._isc_color_btn, isc_s.get("color", "#555555"))
                self._isc_lw_spin.setValue(isc_s.get("linewidth", 1.2))
                self._isc_show_label_cb.setChecked(isc_s.get("show_label", True))
                self._isc_label_edit.setText(isc_s.get("label_text", "ISC"))
                self._isc_label_fs_spin.setValue(isc_s.get("label_fontsize", 9))
                self._isc_curvature_spin.setValue(isc_s.get("curvature", 0.3))
        finally:
            self._updating = False

    # ------------------------------------------------------------------
    # Control → style dict update slots
    # ------------------------------------------------------------------

    def _on_font_changed(self, family: str) -> None:
        if self._updating:
            return
        if not _is_font_available(family):
            logger.warning("Font '%s' not available; keeping %s", family, _FALLBACK_FONT)
            family = _FALLBACK_FONT
            self._updating = True
            self._sync_general_control("font_combo", family, "setCurrentText")
            self._updating = False
        self._current_style["title"]["fontfamily"] = family
        self._current_style["axes"]["label_fontfamily"] = family
        self._current_style["compound_labels"]["fontfamily"] = family
        self._sync_general_control("font_combo", family, "setCurrentText")
        self._schedule_emit()

    def _on_title_size_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["title"]["fontsize"] = value
        self._sync_general_control("title_size_spin", value, "setValue")
        self._schedule_emit()

    def _on_title_text_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["title"]["text"] = text
        self._sync_general_control("title_text_edit", text, "setText")
        self._schedule_emit()

    def _on_ylabel_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["axes"]["ylabel"] = text
        self._sync_general_control("ylabel_edit", text, "setText")
        self._schedule_emit()

    def _on_legend_changed(self, _: int) -> None:
        if self._updating:
            return
        # Find which checkbox actually emitted the signal and read its state
        sender = self.sender()
        checked = sender.isChecked() if sender is not None else False
        self._current_style["legend"]["visible"] = checked
        self._sync_general_control("show_legend_cb", checked, "setChecked")
        self._schedule_emit()

    def _on_grid_changed(self, _: int) -> None:
        if self._updating:
            return
        sender = self.sender()
        checked = sender.isChecked() if sender is not None else False
        self._current_style["axes"]["show_grid"] = checked
        self._sync_general_control("show_grid_cb", checked, "setChecked")
        self._schedule_emit()

    def _on_spine_lw_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["axes"]["spine_linewidth"] = value
        self._sync_general_control("spine_lw_spin", value, "setValue")
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

    def _on_homo_offset_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["homo"]["value_offset_points"] = value
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

    # State level slots

    def _on_state_lw_changed(self, level: str, value: float) -> None:
        if self._updating:
            return
        self._current_style[level]["linewidth"] = value  # type: ignore[index]
        self._schedule_emit()

    def _on_state_val_fs_changed(self, level: str, value: int) -> None:
        if self._updating:
            return
        self._current_style[level]["value_fontsize"] = value  # type: ignore[index]
        self._schedule_emit()

    def _on_state_offset_changed(self, level: str, value: int) -> None:
        if self._updating:
            return
        self._current_style[level]["value_offset_points"] = value  # type: ignore[index]
        self._schedule_emit()

    def _on_state_label_text_changed(self, level: str, text: str) -> None:
        if self._updating:
            return
        self._current_style[level]["label_text"] = text  # type: ignore[index]
        self._schedule_emit()

    def _on_state_label_fs_changed(self, level: str, value: int) -> None:
        if self._updating:
            return
        self._current_style[level]["label_fontsize"] = value  # type: ignore[index]
        self._schedule_emit()

    # Absorption arrow slots

    def _on_abs_lw_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["absorption_arrow"]["linewidth"] = value
        self._schedule_emit()

    def _on_abs_show_label_changed(self, _: int) -> None:
        if self._updating:
            return
        self._current_style["absorption_arrow"]["show_label"] = self._abs_show_label_cb.isChecked()
        self._schedule_emit()

    def _on_abs_label_text_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["absorption_arrow"]["label_text"] = text
        self._schedule_emit()

    def _on_abs_label_fs_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["absorption_arrow"]["label_fontsize"] = value
        self._schedule_emit()

    # ISC curve slots

    def _on_isc_lw_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["isc_curve"]["linewidth"] = value
        self._schedule_emit()

    def _on_isc_show_label_changed(self, _: int) -> None:
        if self._updating:
            return
        self._current_style["isc_curve"]["show_label"] = self._isc_show_label_cb.isChecked()
        self._schedule_emit()

    def _on_isc_label_text_changed(self, text: str) -> None:
        if self._updating:
            return
        self._current_style["isc_curve"]["label_text"] = text
        self._schedule_emit()

    def _on_isc_label_fs_changed(self, value: int) -> None:
        if self._updating:
            return
        self._current_style["isc_curve"]["label_fontsize"] = value
        self._schedule_emit()

    def _on_isc_curvature_changed(self, value: float) -> None:
        if self._updating:
            return
        self._current_style["isc_curve"]["curvature"] = value
        self._schedule_emit()

    # ------------------------------------------------------------------
    # Color picker
    # ------------------------------------------------------------------

    def _pick_color(self, target: str) -> None:
        if target == "bg":
            current = self._current_style["figure"]["background_color"]
            color = QColorDialog.getColor(QColor(current), self, "Choose Color")
            if not color.isValid():
                return
            hex_color = color.name()
            self._current_style["figure"]["background_color"] = hex_color
            for controls in self._general_controls.values():
                self._set_color_btn(controls["bg_color_btn"], hex_color)
            self._schedule_emit()
            return

        if target in ("s0", "s1", "t1"):
            ctrl = self._state_controls[target]
            current = self._current_style[target]["color"]  # type: ignore[index]
            color = QColorDialog.getColor(QColor(current), self, "Choose Color")
            if not color.isValid():
                return
            hex_color = color.name()
            self._current_style[target]["color"] = hex_color  # type: ignore[index]
            self._current_style[target]["value_color"] = hex_color  # type: ignore[index]
            self._current_style[target]["label_color"] = hex_color  # type: ignore[index]
            self._set_color_btn(ctrl["color_btn"], hex_color)
            self._schedule_emit()
            return

        if target == "abs":
            current = self._current_style["absorption_arrow"]["color"]
            color = QColorDialog.getColor(QColor(current), self, "Choose Color")
            if not color.isValid():
                return
            hex_color = color.name()
            self._current_style["absorption_arrow"]["color"] = hex_color
            self._current_style["absorption_arrow"]["label_color"] = hex_color
            self._set_color_btn(self._abs_color_btn, hex_color)
            self._schedule_emit()
            return

        if target == "isc":
            current = self._current_style["isc_curve"]["color"]
            color = QColorDialog.getColor(QColor(current), self, "Choose Color")
            if not color.isValid():
                return
            hex_color = color.name()
            self._current_style["isc_curve"]["color"] = hex_color
            self._current_style["isc_curve"]["label_color"] = hex_color
            self._set_color_btn(self._isc_color_btn, hex_color)
            self._schedule_emit()
            return

        color_map = {
            "homo":  ("homo",      "color",            self._homo_color_btn),
            "lumo":  ("lumo",      "color",            self._lumo_color_btn),
            "arrow": ("gap_arrow", "color",            self._arrow_color_btn),
        }
        section, key, btn = color_map[target]
        current = self._current_style[section][key]  # type: ignore[index]
        color = QColorDialog.getColor(QColor(current), self, "Choose Color")
        if not color.isValid():
            return
        hex_color = color.name()
        self._current_style[section][key] = hex_color  # type: ignore[index]
        if target == "homo":
            self._current_style["homo"]["value_color"] = hex_color
        elif target == "lumo":
            self._current_style["lumo"]["value_color"] = hex_color
        self._set_color_btn(btn, hex_color)
        self._schedule_emit()

    def _set_color_btn(self, btn: QPushButton, hex_color: str) -> None:
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
            if "figure" in style and "figsize" in style["figure"]:
                style["figure"]["figsize"] = tuple(style["figure"]["figsize"])
            self.set_style(style)
            self._emit_style_changed()
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            QMessageBox.critical(self, "Import Error", f"Could not load style: {exc}")
