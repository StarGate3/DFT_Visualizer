"""Publication-quality export dialog for DFT Visualizer."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QComboBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FORMATS = ["PNG", "TIFF", "SVG", "PDF"]
_FORMAT_LABELS = [
    "PNG (lossless, recommended for slides/web)",
    "TIFF (lossless, recommended for print publications)",
    "SVG (vector, scalable)",
    "PDF (vector, for LaTeX)",
]
_FORMAT_KEYS = ["png", "tiff", "svg", "pdf"]

_DPI_VALUES = [300, 600, 1200, None]  # None = custom
_DPI_LABELS = [
    "300 DPI (standard print)",
    "600 DPI (high-quality print — recommended for publications)",
    "1200 DPI (maximum quality)",
    "Custom…",
]

_FIGSIZE_VALUES: list[Optional[tuple[float, float]]] = [
    None,
    (8.9, 6.5),
    (18.3, 9.0),
    (8.3, 6.0),
    (17.1, 8.5),
    (29.7, 21.0),
    (28.0, 21.6),
    (15.0, 15.0),
    None,  # custom (last index)
]
_FIGSIZE_LABELS = [
    "Current (as shown)",
    "Nature single column (8.9 × 6.5 cm)",
    "Nature double column (18.3 × 9.0 cm)",
    "JACS single column (8.3 × 6.0 cm)",
    "JACS double column (17.1 × 8.5 cm)",
    "A4 landscape (29.7 × 21.0 cm)",
    "Letter landscape (28.0 × 21.6 cm)",
    "Square (15 × 15 cm)",
    "Custom…",
]
_FIGSIZE_CUSTOM_IDX = len(_FIGSIZE_LABELS) - 1

_TIFF_COMPRESSION_LABELS = [
    "LZW (lossless, recommended)",
    "Deflate (lossless)",
    "None (largest files)",
]
_TIFF_COMPRESSION_KEYS = ["lzw", "deflate", "none"]

_VECTOR_FORMATS = {"svg", "pdf"}


class ExportDialog(QDialog):
    """Dialog for configuring and triggering publication-quality figure export."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Diagram")
        self.setMinimumWidth(520)
        self._settings = QSettings("DFTVisualizer", "ExportDialog")
        self._setup_ui()
        self._connect_signals()
        self._load_settings()
        self._update_ui_state()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setSpacing(8)

        main.addWidget(self._build_scope_group())
        main.addWidget(self._build_format_group())
        main.addWidget(self._build_figsize_group())
        main.addWidget(self._build_background_group())
        main.addWidget(self._build_tiff_group())
        main.addWidget(self._build_output_group())

        # Buttons
        btns = QDialogButtonBox()
        self._cancel_btn = btns.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._export_btn = btns.addButton("Export", QDialogButtonBox.ButtonRole.AcceptRole)
        self._export_btn.setDefault(True)
        btns.rejected.connect(self.reject)
        self._export_btn.clicked.connect(self._on_export_clicked)
        main.addWidget(btns)

    def _build_scope_group(self) -> QGroupBox:
        gb = QGroupBox("What to export")
        layout = QVBoxLayout(gb)
        self._scope_active = QRadioButton("Active diagram only")
        self._scope_all = QRadioButton("All diagrams (one file per tab)")
        self._scope_active.setChecked(True)
        self._scope_group = QButtonGroup(self)
        self._scope_group.addButton(self._scope_active, 0)
        self._scope_group.addButton(self._scope_all, 1)
        layout.addWidget(self._scope_active)
        layout.addWidget(self._scope_all)
        return gb

    def _build_format_group(self) -> QGroupBox:
        gb = QGroupBox("Format & Resolution")
        form = QFormLayout(gb)

        self._format_combo = QComboBox()
        self._format_combo.addItems(_FORMAT_LABELS)
        form.addRow("Format:", self._format_combo)

        dpi_row = QWidget()
        dpi_layout = QHBoxLayout(dpi_row)
        dpi_layout.setContentsMargins(0, 0, 0, 0)
        self._dpi_combo = QComboBox()
        self._dpi_combo.addItems(_DPI_LABELS)
        self._dpi_combo.setCurrentIndex(1)  # default 600
        dpi_layout.addWidget(self._dpi_combo, 1)
        self._dpi_spin = QSpinBox()
        self._dpi_spin.setRange(72, 2400)
        self._dpi_spin.setSingleStep(50)
        self._dpi_spin.setValue(600)
        self._dpi_spin.setVisible(False)
        dpi_layout.addWidget(self._dpi_spin)
        form.addRow("Resolution:", dpi_row)

        self._dpi_hint = QLabel("DPI not applicable for vector formats.")
        self._dpi_hint.setStyleSheet("color: #888888; font-style: italic;")
        self._dpi_hint.setVisible(False)
        form.addRow("", self._dpi_hint)

        self._tiff_compression_label = QLabel("Compression:")
        self._tiff_compression_combo = QComboBox()
        self._tiff_compression_combo.addItems(_TIFF_COMPRESSION_LABELS)
        form.addRow(self._tiff_compression_label, self._tiff_compression_combo)

        return gb

    def _build_figsize_group(self) -> QGroupBox:
        gb = QGroupBox("Figure size")
        form = QFormLayout(gb)

        self._figsize_combo = QComboBox()
        self._figsize_combo.addItems(_FIGSIZE_LABELS)
        form.addRow("Size preset:", self._figsize_combo)

        custom_row = QWidget()
        cr_layout = QHBoxLayout(custom_row)
        cr_layout.setContentsMargins(0, 0, 0, 0)
        self._figsize_w_spin = QDoubleSpinBox()
        self._figsize_w_spin.setRange(3.0, 50.0)
        self._figsize_w_spin.setSingleStep(0.5)
        self._figsize_w_spin.setDecimals(1)
        self._figsize_w_spin.setValue(15.0)
        self._figsize_w_spin.setSuffix(" cm")
        self._figsize_h_spin = QDoubleSpinBox()
        self._figsize_h_spin.setRange(3.0, 50.0)
        self._figsize_h_spin.setSingleStep(0.5)
        self._figsize_h_spin.setDecimals(1)
        self._figsize_h_spin.setValue(10.0)
        self._figsize_h_spin.setSuffix(" cm")
        cr_layout.addWidget(QLabel("W:"))
        cr_layout.addWidget(self._figsize_w_spin, 1)
        cr_layout.addWidget(QLabel("H:"))
        cr_layout.addWidget(self._figsize_h_spin, 1)
        self._figsize_custom_row = custom_row
        form.addRow("Custom:", custom_row)

        return gb

    def _build_background_group(self) -> QGroupBox:
        gb = QGroupBox("Background")
        layout = QVBoxLayout(gb)
        self._bg_white = QRadioButton("White")
        self._bg_transparent = QRadioButton("Transparent (PNG/SVG/PDF only)")
        self._bg_style = QRadioButton("From style preset")
        self._bg_white.setChecked(True)
        bg_group = QButtonGroup(self)
        bg_group.addButton(self._bg_white, 0)
        bg_group.addButton(self._bg_transparent, 1)
        bg_group.addButton(self._bg_style, 2)
        self._bg_button_group = bg_group
        layout.addWidget(self._bg_white)
        layout.addWidget(self._bg_transparent)
        layout.addWidget(self._bg_style)
        return gb

    def _build_tiff_group(self) -> QGroupBox:
        # TIFF compression is now inside the format group — this group is unused
        # but kept as a hidden placeholder to avoid index errors.
        gb = QGroupBox()
        gb.setVisible(False)
        return gb

    def _build_output_group(self) -> QGroupBox:
        gb = QGroupBox("Output location")
        form = QFormLayout(gb)

        folder_row = QWidget()
        fr_layout = QHBoxLayout(folder_row)
        fr_layout.setContentsMargins(0, 0, 0, 0)
        self._folder_edit = QLineEdit()
        self._folder_edit.setReadOnly(True)
        self._folder_edit.setPlaceholderText("(choose a folder)")
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(72)
        browse_btn.clicked.connect(self._browse_folder)
        fr_layout.addWidget(self._folder_edit, 1)
        fr_layout.addWidget(browse_btn)
        form.addRow("Output folder:", folder_row)

        self._filename_edit = QLineEdit()
        self._filename_edit.setPlaceholderText("filename (without extension)")
        form.addRow("Filename:", self._filename_edit)

        self._all_preview_label = QLabel()
        self._all_preview_label.setStyleSheet("color: #555555; font-style: italic;")
        self._all_preview_label.setWordWrap(True)
        self._all_preview_label.setVisible(False)
        form.addRow("", self._all_preview_label)

        return gb

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._format_combo.currentIndexChanged.connect(self._update_ui_state)
        self._dpi_combo.currentIndexChanged.connect(self._update_ui_state)
        self._figsize_combo.currentIndexChanged.connect(self._update_ui_state)
        self._scope_group.idToggled.connect(self._update_ui_state)
        self._filename_edit.textChanged.connect(self._update_preview)

    # ------------------------------------------------------------------
    # Dynamic UI updates
    # ------------------------------------------------------------------

    def _update_ui_state(self, *_: object) -> None:
        fmt = _FORMAT_KEYS[self._format_combo.currentIndex()]
        is_vector = fmt in _VECTOR_FORMATS
        is_tiff = fmt == "tiff"
        is_custom_dpi = self._dpi_combo.currentIndex() == 3

        self._dpi_combo.setEnabled(not is_vector)
        self._dpi_spin.setEnabled(not is_vector and is_custom_dpi)
        self._dpi_spin.setVisible(is_custom_dpi and not is_vector)
        self._dpi_hint.setVisible(is_vector)

        self._tiff_compression_label.setVisible(is_tiff)
        self._tiff_compression_combo.setVisible(is_tiff)

        is_custom_size = self._figsize_combo.currentIndex() == _FIGSIZE_CUSTOM_IDX
        self._figsize_custom_row.setVisible(is_custom_size)

        is_all = self._scope_all.isChecked()
        self._all_preview_label.setVisible(is_all)
        self._update_preview()

    def _update_preview(self, *_: object) -> None:
        if not self._scope_all.isChecked():
            return
        base = self._filename_edit.text().strip() or "<filename>"
        ext = _FORMAT_KEYS[self._format_combo.currentIndex()]
        self._all_preview_label.setText(
            f"Files: {base}_homo_lumo.{ext},  {base}_states.{ext},  "
            f"{base}_franck_condon.{ext}"
        )

    # ------------------------------------------------------------------
    # Folder browser
    # ------------------------------------------------------------------

    def _browse_folder(self) -> None:
        start = self._folder_edit.text() or str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder", start)
        if folder:
            self._folder_edit.setText(folder)

    # ------------------------------------------------------------------
    # Validation + Export trigger
    # ------------------------------------------------------------------

    def _on_export_clicked(self) -> None:
        folder_text = self._folder_edit.text().strip()
        filename_text = self._filename_edit.text().strip()

        if not folder_text:
            QMessageBox.critical(self, "Missing output folder",
                                 "Please choose an output folder.")
            return
        folder = Path(folder_text)
        if not folder.is_dir():
            QMessageBox.critical(self, "Folder not found",
                                 f"Output folder does not exist:\n{folder}")
            return
        if not filename_text:
            QMessageBox.critical(self, "Missing filename",
                                 "Please enter a filename (without extension).")
            return
        if self._dpi_spin.isVisible():
            dpi = self._dpi_spin.value()
            if not (72 <= dpi <= 2400):
                QMessageBox.critical(self, "Invalid DPI",
                                     "Custom DPI must be between 72 and 2400.")
                return

        self._save_settings()
        self.accept()

    # ------------------------------------------------------------------
    # QSettings persistence
    # ------------------------------------------------------------------

    def _load_settings(self) -> None:
        self._folder_edit.setText(
            self._settings.value("output_folder", str(Path.home()), str)
        )
        self._filename_edit.setText(
            self._settings.value("filename", "diagram", str)
        )
        self._format_combo.setCurrentIndex(
            int(self._settings.value("format_index", 1))  # TIFF default
        )
        self._dpi_combo.setCurrentIndex(
            int(self._settings.value("dpi_index", 1))  # 600 DPI default
        )
        self._dpi_spin.setValue(int(self._settings.value("custom_dpi", 600)))
        self._figsize_combo.setCurrentIndex(
            int(self._settings.value("figsize_index", 0))
        )
        self._figsize_w_spin.setValue(float(self._settings.value("custom_w", 15.0)))
        self._figsize_h_spin.setValue(float(self._settings.value("custom_h", 10.0)))
        bg_id = int(self._settings.value("background_id", 0))
        btn = self._bg_button_group.button(bg_id)
        if btn:
            btn.setChecked(True)
        self._tiff_compression_combo.setCurrentIndex(
            int(self._settings.value("tiff_compression_index", 0))
        )
        scope_all = self._settings.value("scope_all", False, bool)
        self._scope_all.setChecked(bool(scope_all))
        self._scope_active.setChecked(not bool(scope_all))

    def _save_settings(self) -> None:
        self._settings.setValue("output_folder", self._folder_edit.text())
        self._settings.setValue("filename", self._filename_edit.text().strip())
        self._settings.setValue("format_index", self._format_combo.currentIndex())
        self._settings.setValue("dpi_index", self._dpi_combo.currentIndex())
        self._settings.setValue("custom_dpi", self._dpi_spin.value())
        self._settings.setValue("figsize_index", self._figsize_combo.currentIndex())
        self._settings.setValue("custom_w", self._figsize_w_spin.value())
        self._settings.setValue("custom_h", self._figsize_h_spin.value())
        self._settings.setValue(
            "background_id", self._bg_button_group.checkedId()
        )
        self._settings.setValue(
            "tiff_compression_index", self._tiff_compression_combo.currentIndex()
        )
        self._settings.setValue("scope_all", self._scope_all.isChecked())

    # ------------------------------------------------------------------
    # Result getters (called by MainWindow after dialog.exec() == Accepted)
    # ------------------------------------------------------------------

    def get_scope(self) -> str:
        return "all" if self._scope_all.isChecked() else "active"

    def get_format(self) -> str:
        return _FORMAT_KEYS[self._format_combo.currentIndex()]

    def get_dpi(self) -> int:
        idx = self._dpi_combo.currentIndex()
        if idx == 3:
            return self._dpi_spin.value()
        return _DPI_VALUES[idx]  # type: ignore[return-value]

    def get_figsize_cm(self) -> Optional[tuple[float, float]]:
        idx = self._figsize_combo.currentIndex()
        if idx == 0:
            return None  # current size
        if idx == _FIGSIZE_CUSTOM_IDX:
            return (self._figsize_w_spin.value(), self._figsize_h_spin.value())
        return _FIGSIZE_VALUES[idx]

    def get_background(self) -> str:
        bid = self._bg_button_group.checkedId()
        return {0: "white", 1: "transparent", 2: "style"}.get(bid, "white")

    def get_tiff_compression(self) -> str:
        return _TIFF_COMPRESSION_KEYS[self._tiff_compression_combo.currentIndex()]

    def get_output_folder(self) -> Path:
        return Path(self._folder_edit.text().strip())

    def get_filename(self) -> str:
        return self._filename_edit.text().strip()
