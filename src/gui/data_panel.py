"""Data loading and editing panel for DFT Visualizer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.data.excel_parser import ExcelParsingError, parse_excel
from src.data.models import (
    CompoundFranckCondon,
    CompoundHomoLumo,
    CompoundStates,
    DFTDataset,
)
from src.data.validator import validate_dataset

_GAP_BG = QColor("#dcdcdc")
_FC_STATES = ["S0", "S1", "T1"]


# ---------------------------------------------------------------------------
# Custom delegates
# ---------------------------------------------------------------------------


class _NumericDelegate(QStyledItemDelegate):
    """QDoubleSpinBox-based delegate for numeric table cells."""

    def __init__(
        self,
        minimum: float = -1000.0,
        maximum: float = 1000.0,
        decimals: int = 4,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._min = minimum
        self._max = maximum
        self._decimals = decimals

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QDoubleSpinBox:
        editor = QDoubleSpinBox(parent)
        editor.setRange(self._min, self._max)
        editor.setDecimals(self._decimals)
        editor.setSingleStep(0.01)
        editor.setFrame(False)
        return editor

    def setEditorData(self, editor: QDoubleSpinBox, index: QModelIndex) -> None:  # type: ignore[override]
        text = index.data(Qt.ItemDataRole.EditRole)
        try:
            editor.setValue(float(text) if text else 0.0)
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(
        self,
        editor: QDoubleSpinBox,  # type: ignore[override]
        model: QAbstractItemModel,
        index: QModelIndex,
    ) -> None:
        editor.interpretText()
        model.setData(index, f"{editor.value():.4f}", Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(
        self,
        editor: QDoubleSpinBox,  # type: ignore[override]
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        editor.setGeometry(option.rect)


class _StateComboDelegate(QStyledItemDelegate):
    """QComboBox-based delegate for the FC State column."""

    def createEditor(
        self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex
    ) -> QComboBox:
        editor = QComboBox(parent)
        editor.addItems(_FC_STATES)
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex) -> None:  # type: ignore[override]
        value = index.data(Qt.ItemDataRole.EditRole) or _FC_STATES[0]
        idx = editor.findText(value)
        editor.setCurrentIndex(max(0, idx))

    def setModelData(
        self,
        editor: QComboBox,  # type: ignore[override]
        model: QAbstractItemModel,
        index: QModelIndex,
    ) -> None:
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(
        self,
        editor: QComboBox,  # type: ignore[override]
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        editor.setGeometry(option.rect)


# ---------------------------------------------------------------------------
# DataPanel
# ---------------------------------------------------------------------------


class DataPanel(QWidget):
    """Left-dock panel for loading, viewing, and editing DFT calculation data.

    Signals:
        data_changed: Emitted whenever the user edits a cell, adds, or removes
            a row.  Plot widgets subscribe to this in Stage 3+.
        status_message: Emits a string to be displayed on the main window's
            status bar (e.g. after a successful Excel import).
    """

    data_changed = pyqtSignal()
    status_message = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._loading: bool = False
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self._build_toolbar(layout)
        self._build_tabs(layout)

    def _build_toolbar(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        row.setSpacing(4)

        load_btn = QPushButton("Load from Excel…")
        load_btn.setToolTip("Import data from an .xlsx file")
        load_btn.clicked.connect(self.load_from_excel)

        validate_btn = QPushButton("Validate Data")
        validate_btn.setToolTip("Check data for common issues")
        validate_btn.clicked.connect(self._validate_data)

        clear_btn = QPushButton("Clear All Data")
        clear_btn.setToolTip("Remove all rows from all tables")
        clear_btn.clicked.connect(self._clear_all_data)

        row.addWidget(load_btn)
        row.addWidget(validate_btn)
        row.addWidget(clear_btn)
        row.addStretch()
        parent_layout.addLayout(row)

    def _build_tabs(self, parent_layout: QVBoxLayout) -> None:
        self._tabs = QTabWidget()
        self._homo_lumo_table = self._build_homo_lumo_tab()
        self._states_table = self._build_states_tab()
        self._fc_table = self._build_fc_tab()
        parent_layout.addWidget(self._tabs)

    # ---- HOMO/LUMO tab -----------------------------------------------

    def _build_homo_lumo_tab(self) -> QTableWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(2)

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(
            ["Compound Name", "HOMO (eV)", "LUMO (eV)", "Gap (eV)"]
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for col in (1, 2, 3):
            table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setAlternatingRowColors(True)

        num_delegate = _NumericDelegate(parent=table)
        table.setItemDelegateForColumn(1, num_delegate)
        table.setItemDelegateForColumn(2, num_delegate)

        table.itemChanged.connect(self._on_homo_lumo_changed)

        vbox.addWidget(table)
        vbox.addLayout(self._build_row_buttons(table, "homo_lumo"))
        self._tabs.addTab(container, "HOMO/LUMO")
        return table

    # ---- States tab --------------------------------------------------

    def _build_states_tab(self) -> QTableWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(2)

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(
            ["Compound Name", "S0 (eV)", "S1 (eV)", "T1 (eV)"]
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for col in (1, 2, 3):
            table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setAlternatingRowColors(True)

        num_delegate = _NumericDelegate(minimum=0.0, parent=table)
        for col in (1, 2, 3):
            table.setItemDelegateForColumn(col, num_delegate)

        table.itemChanged.connect(self._on_generic_changed)

        vbox.addWidget(table)
        vbox.addLayout(self._build_row_buttons(table, "states"))
        self._tabs.addTab(container, "States")
        return table

    # ---- Franck-Condon tab -------------------------------------------

    def _build_fc_tab(self) -> QTableWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(2)

        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(
            [
                "Compound Name",
                "State",
                "E_vertical",
                "E_adiabatic",
                "BDE Value",
                "BDE Label",
            ]
        )
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        for col in (2, 3, 4):
            table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.ResizeToContents
        )
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setAlternatingRowColors(True)

        table.setItemDelegateForColumn(1, _StateComboDelegate(table))
        e_delegate = _NumericDelegate(minimum=0.0, maximum=2000.0, parent=table)
        table.setItemDelegateForColumn(2, e_delegate)
        table.setItemDelegateForColumn(3, e_delegate)
        bde_delegate = _NumericDelegate(minimum=0.0, maximum=2000.0, parent=table)
        table.setItemDelegateForColumn(4, bde_delegate)

        table.itemChanged.connect(self._on_generic_changed)

        vbox.addWidget(table)
        vbox.addLayout(self._build_row_buttons(table, "fc"))
        self._tabs.addTab(container, "Franck-Condon")
        return table

    # ---- Shared button row -------------------------------------------

    def _build_row_buttons(
        self, table: QTableWidget, tab_id: str
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(4)

        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(lambda: self._add_row(table, tab_id))

        remove_btn = QPushButton("Remove Selected Row")
        remove_btn.clicked.connect(lambda: self._remove_row(table))

        dup_btn = QPushButton("Duplicate Row")
        dup_btn.clicked.connect(lambda: self._duplicate_row(table, tab_id))

        row.addWidget(add_btn)
        row.addWidget(remove_btn)
        row.addWidget(dup_btn)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    # Gap column helpers
    # ------------------------------------------------------------------

    def _make_gap_item(self, value: float) -> QTableWidgetItem:
        item = QTableWidgetItem(f"{value:.4f}")
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setBackground(QBrush(_GAP_BG))
        return item

    def _recalculate_gap(self, row: int) -> None:
        homo_item = self._homo_lumo_table.item(row, 1)
        lumo_item = self._homo_lumo_table.item(row, 2)
        if homo_item is None or lumo_item is None:
            return
        try:
            gap = float(lumo_item.text()) - float(homo_item.text())
        except ValueError:
            return
        self._homo_lumo_table.blockSignals(True)
        self._homo_lumo_table.setItem(row, 3, self._make_gap_item(gap))
        self._homo_lumo_table.blockSignals(False)

    # ------------------------------------------------------------------
    # itemChanged handlers
    # ------------------------------------------------------------------

    def _on_homo_lumo_changed(self, item: QTableWidgetItem) -> None:
        if self._loading:
            return
        if item.column() in (1, 2):
            self._recalculate_gap(item.row())
        self.data_changed.emit()

    def _on_generic_changed(self, item: QTableWidgetItem) -> None:
        if self._loading:
            return
        self.data_changed.emit()

    # ------------------------------------------------------------------
    # Row manipulation
    # ------------------------------------------------------------------

    def _add_row(self, table: QTableWidget, tab_id: str) -> None:
        self._loading = True
        try:
            r = table.rowCount()
            table.insertRow(r)
            if tab_id == "homo_lumo":
                table.setItem(r, 0, QTableWidgetItem(""))
                table.setItem(r, 1, QTableWidgetItem("0.0000"))
                table.setItem(r, 2, QTableWidgetItem("0.0000"))
                table.setItem(r, 3, self._make_gap_item(0.0))
            elif tab_id == "states":
                table.setItem(r, 0, QTableWidgetItem(""))
                for col in (1, 2, 3):
                    table.setItem(r, col, QTableWidgetItem("0.0000"))
            else:  # fc
                table.setItem(r, 0, QTableWidgetItem(""))
                table.setItem(r, 1, QTableWidgetItem("S0"))
                for col in (2, 3):
                    table.setItem(r, col, QTableWidgetItem("0.0000"))
                table.setItem(r, 4, QTableWidgetItem(""))
                table.setItem(r, 5, QTableWidgetItem(""))
        finally:
            self._loading = False
        self.data_changed.emit()

    def _remove_row(self, table: QTableWidget) -> None:
        rows = sorted(
            {idx.row() for idx in table.selectedIndexes()}, reverse=True
        )
        if not rows:
            return
        for r in rows:
            table.removeRow(r)
        self.data_changed.emit()

    def _duplicate_row(self, table: QTableWidget, tab_id: str) -> None:
        rows = sorted({idx.row() for idx in table.selectedIndexes()})
        if not rows:
            return
        self._loading = True
        try:
            for src_row in reversed(rows):
                dest_row = src_row + 1
                table.insertRow(dest_row)
                col_count = table.columnCount()
                for col in range(col_count):
                    src_item = table.item(src_row, col)
                    text = src_item.text() if src_item else ""
                    if tab_id == "homo_lumo" and col == 3:
                        table.setItem(dest_row, col, self._make_gap_item(
                            float(text) if text else 0.0
                        ))
                    else:
                        new_item = QTableWidgetItem(text)
                        table.setItem(dest_row, col, new_item)
        finally:
            self._loading = False
        self.data_changed.emit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_dataset(self) -> DFTDataset:
        """Read current table state and return a DFTDataset.

        Empty compound-name rows are skipped.  Non-parseable numeric cells
        default to 0.0.

        Returns:
            A :class:`DFTDataset` reflecting the current table contents.
        """
        homo_lumo: list[CompoundHomoLumo] = []
        for r in range(self._homo_lumo_table.rowCount()):
            name = self._cell_text(self._homo_lumo_table, r, 0)
            if not name:
                continue
            homo = self._cell_float(self._homo_lumo_table, r, 1)
            lumo = self._cell_float(self._homo_lumo_table, r, 2)
            homo_lumo.append(CompoundHomoLumo(name=name, homo=homo, lumo=lumo))

        states: list[CompoundStates] = []
        for r in range(self._states_table.rowCount()):
            name = self._cell_text(self._states_table, r, 0)
            if not name:
                continue
            states.append(CompoundStates(
                name=name,
                s0=self._cell_float(self._states_table, r, 1),
                s1=self._cell_float(self._states_table, r, 2),
                t1=self._cell_float(self._states_table, r, 3),
            ))

        fc: list[CompoundFranckCondon] = []
        for r in range(self._fc_table.rowCount()):
            name = self._cell_text(self._fc_table, r, 0)
            if not name:
                continue
            bde_val_text = self._cell_text(self._fc_table, r, 4)
            bde_lbl_text = self._cell_text(self._fc_table, r, 5)
            bde_value: Optional[float] = None
            if bde_val_text:
                try:
                    bde_value = float(bde_val_text)
                except ValueError:
                    pass
            fc.append(CompoundFranckCondon(
                name=name,
                state=self._cell_text(self._fc_table, r, 1) or "S0",
                e_vertical=self._cell_float(self._fc_table, r, 2),
                e_adiabatic=self._cell_float(self._fc_table, r, 3),
                bde_value=bde_value,
                bde_label=bde_lbl_text or None,
            ))

        return DFTDataset(homo_lumo=homo_lumo, states=states, franck_condon=fc)

    def set_dataset(self, dataset: DFTDataset) -> None:
        """Populate all three tables from a DFTDataset.

        Does not emit :attr:`data_changed`; callers are responsible for
        emitting it if required.

        Args:
            dataset: The dataset to display.
        """
        self._loading = True
        try:
            self._homo_lumo_table.setRowCount(0)
            for c in dataset.homo_lumo:
                r = self._homo_lumo_table.rowCount()
                self._homo_lumo_table.insertRow(r)
                self._homo_lumo_table.setItem(r, 0, QTableWidgetItem(c.name))
                self._homo_lumo_table.setItem(r, 1, QTableWidgetItem(str(c.homo)))
                self._homo_lumo_table.setItem(r, 2, QTableWidgetItem(str(c.lumo)))
                self._homo_lumo_table.setItem(r, 3, self._make_gap_item(c.gap))

            self._states_table.setRowCount(0)
            for c in dataset.states:
                r = self._states_table.rowCount()
                self._states_table.insertRow(r)
                self._states_table.setItem(r, 0, QTableWidgetItem(c.name))
                self._states_table.setItem(r, 1, QTableWidgetItem(str(c.s0)))
                self._states_table.setItem(r, 2, QTableWidgetItem(str(c.s1)))
                self._states_table.setItem(r, 3, QTableWidgetItem(str(c.t1)))

            self._fc_table.setRowCount(0)
            for entry in dataset.franck_condon:
                r = self._fc_table.rowCount()
                self._fc_table.insertRow(r)
                self._fc_table.setItem(r, 0, QTableWidgetItem(entry.name))
                self._fc_table.setItem(r, 1, QTableWidgetItem(entry.state))
                self._fc_table.setItem(r, 2, QTableWidgetItem(str(entry.e_vertical)))
                self._fc_table.setItem(r, 3, QTableWidgetItem(str(entry.e_adiabatic)))
                self._fc_table.setItem(
                    r, 4,
                    QTableWidgetItem(str(entry.bde_value) if entry.bde_value is not None else "")
                )
                self._fc_table.setItem(
                    r, 5,
                    QTableWidgetItem(entry.bde_label if entry.bde_label is not None else "")
                )
        finally:
            self._loading = False

    def load_from_excel(self) -> None:
        """Open a file dialog and load data from a selected .xlsx file.

        On success: populates the tables, switches to the HOMO/LUMO tab, and
        emits :attr:`status_message` with a summary.
        On failure: shows a QMessageBox with the parsing error.
        """
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import Excel File",
            "",
            "Excel Files (*.xlsx);;All Files (*)",
        )
        if not filepath:
            return

        path = Path(filepath)
        try:
            dataset = parse_excel(path)
        except ExcelParsingError as exc:
            QMessageBox.critical(self, "Import Error", str(exc))
            return

        self.set_dataset(dataset)
        self._tabs.setCurrentIndex(0)
        n = len(dataset.homo_lumo)
        self.status_message.emit(f"Loaded {n} compounds from {path.name}")

    # ------------------------------------------------------------------
    # Toolbar button handlers
    # ------------------------------------------------------------------

    def _validate_data(self) -> None:
        issues = validate_dataset(self.get_dataset())
        if not issues:
            QMessageBox.information(self, "Validation", "No issues found.")
            return
        lines: list[str] = []
        for w in issues:
            tag = "[ERROR]" if w.severity == "error" else "[WARN] "
            comp = f" ({w.compound_name})" if w.compound_name else ""
            lines.append(f"{tag} [{w.sheet}]{comp}: {w.message}")
        QMessageBox.warning(self, "Validation Results", "\n".join(lines))

    def _clear_all_data(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear All Data",
            "Are you sure you want to remove all data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.set_dataset(DFTDataset.empty())
            self.data_changed.emit()

    # ------------------------------------------------------------------
    # Cell reading helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cell_text(table: QTableWidget, row: int, col: int) -> str:
        item = table.item(row, col)
        return item.text().strip() if item else ""

    @staticmethod
    def _cell_float(table: QTableWidget, row: int, col: int) -> float:
        item = table.item(row, col)
        if item is None:
            return 0.0
        try:
            return float(item.text())
        except ValueError:
            return 0.0
