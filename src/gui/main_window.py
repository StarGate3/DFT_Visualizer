"""Main application window for DFT Visualizer."""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QCloseEvent, QDesktopServices, QFont, QIcon
from PyQt6.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QFileDialog,
    QStatusBar,
    QTabWidget,
    QWidget,
)

from src.data.models import DFTDataset
from src.data.project_io import load_project, save_project
from src.gui.data_panel import DataPanel
from src.gui.diagram_widgets.franck_condon_diagram import FranckCondonDiagramWidget
from src.gui.diagram_widgets.homo_lumo_diagram import HomoLumoDiagramWidget
from src.gui.diagram_widgets.state_diagram import StateDiagramWidget
from src.gui.export_dialog import ExportDialog
from src.gui.style_panel import StylePanel
from src.plotting.style_presets import DEFAULT_STYLE

logger = logging.getLogger(__name__)

_PROJECT_FILTER = "DFT Visualizer Project (*.dftviz);;All Files (*)"


class MainWindow(QMainWindow):
    """Primary window of the DFT Visualizer application."""

    WINDOW_TITLE: str = "DFT Visualizer"
    DEFAULT_WIDTH: int = 1400
    DEFAULT_HEIGHT: int = 900
    MIN_WIDTH: int = 1000
    MIN_HEIGHT: int = 700

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_project_path: Optional[Path] = None
        self._dirty: bool = False
        self._setup_window()
        self._build_menu_bar()
        self._build_central_widget()
        self._build_dock_widgets()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        self.setWindowTitle(self.WINDOW_TITLE + " \u2014 Untitled")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.setWindowIcon(QIcon())

    def _update_window_title(self) -> None:
        if self._current_project_path is not None:
            name = self._current_project_path.stem
        else:
            name = "Untitled"
        dirty_marker = " \u25cf" if self._dirty else ""
        self.setWindowTitle(f"{self.WINDOW_TITLE} \u2014 {name}{dirty_marker}")

    def _mark_dirty(self) -> None:
        if not self._dirty:
            self._dirty = True
            self._update_window_title()

    def _mark_clean(self) -> None:
        self._dirty = False
        self._update_window_title()

    # ------------------------------------------------------------------
    # Close event — prompt to save unsaved changes
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if reply == QMessageBox.StandardButton.Save:
                if not self._save_project():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        event.accept()

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------

    def _build_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        assert menu_bar is not None
        self._build_file_menu(menu_bar)
        self._build_edit_menu(menu_bar)
        self._build_view_menu(menu_bar)
        self._build_help_menu(menu_bar)

    def _build_file_menu(self, menu_bar: object) -> None:
        file_menu: QMenu = menu_bar.addMenu("&File")  # type: ignore[attr-defined]

        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Project\u2026", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Project &As\u2026", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._on_save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        import_action = QAction("&Import Excel\u2026", self)
        import_action.setShortcut("Ctrl+I")
        self._import_action = import_action
        file_menu.addAction(import_action)

        export_action = QAction("E&xport Diagram\u2026", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_diagram)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _build_edit_menu(self, menu_bar: object) -> None:
        edit_menu: QMenu = menu_bar.addMenu("&Edit")  # type: ignore[attr-defined]

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setEnabled(False)
        edit_menu.addAction(redo_action)

        self._undo_action = undo_action
        self._redo_action = redo_action

    def _build_view_menu(self, menu_bar: object) -> None:
        view_menu: QMenu = menu_bar.addMenu("&View")  # type: ignore[attr-defined]

        self._toggle_data_action = QAction("Toggle &Data Panel", self)
        self._toggle_data_action.setCheckable(True)
        self._toggle_data_action.setChecked(True)
        view_menu.addAction(self._toggle_data_action)

        self._toggle_style_action = QAction("Toggle &Style Panel", self)
        self._toggle_style_action.setCheckable(True)
        self._toggle_style_action.setChecked(True)
        view_menu.addAction(self._toggle_style_action)

    def _build_help_menu(self, menu_bar: object) -> None:
        help_menu: QMenu = menu_bar.addMenu("&Help")  # type: ignore[attr-defined]

        about_action = QAction("&About", self)
        about_action.triggered.connect(lambda: self._show_about())
        help_menu.addAction(about_action)

    # ------------------------------------------------------------------
    # Central widget
    # ------------------------------------------------------------------

    def _build_central_widget(self) -> None:
        self._tab_widget = QTabWidget(self)
        self.setCentralWidget(self._tab_widget)

        self._homo_lumo_widget = HomoLumoDiagramWidget(self)
        self._tab_widget.addTab(self._homo_lumo_widget, "HOMO/LUMO")

        self._state_diagram_widget = StateDiagramWidget(self)
        self._tab_widget.addTab(self._state_diagram_widget, "S0/S1/T1 States")

        self._franck_condon_widget = FranckCondonDiagramWidget(self)
        self._tab_widget.addTab(self._franck_condon_widget, "Franck-Condon")

    def _make_placeholder_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        label.setFont(font)
        label.setStyleSheet("color: #888888;")
        return label

    # ------------------------------------------------------------------
    # Dock widgets
    # ------------------------------------------------------------------

    def _build_dock_widgets(self) -> None:
        allowed_areas = (
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._data_dock = QDockWidget("Data", self)
        self._data_dock.setAllowedAreas(allowed_areas)
        self._data_panel = DataPanel(self)
        self._data_dock.setWidget(self._data_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._data_dock)

        self._import_action.triggered.connect(self._data_panel.load_from_excel)
        self._data_panel.status_message.connect(self._show_status)
        self._data_panel.data_changed.connect(self._on_data_changed)

        self._style_dock = QDockWidget("Style & Appearance", self)
        self._style_dock.setAllowedAreas(allowed_areas)
        self._style_panel = StylePanel(self)
        self._style_dock.setWidget(self._style_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._style_dock)

        self._data_panel.data_changed.connect(self.refresh_active_diagram)
        self._data_panel.dataset_loaded.connect(self.refresh_active_diagram)
        self._data_panel.dataset_loaded.connect(self._mark_dirty)
        self._style_panel.style_changed.connect(self.refresh_active_diagram)
        self._style_panel.style_changed.connect(self._mark_dirty)
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

        self._toggle_data_action.toggled.connect(self._data_dock.setVisible)
        self._toggle_style_action.toggled.connect(self._style_dock.setVisible)
        self._data_dock.visibilityChanged.connect(self._toggle_data_action.setChecked)
        self._style_dock.visibilityChanged.connect(self._toggle_style_action.setChecked)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _build_status_bar(self) -> None:
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    def _show_status(self, message: str) -> None:
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(message)

    # ------------------------------------------------------------------
    # Diagram refresh
    # ------------------------------------------------------------------

    def _on_data_changed(self) -> None:
        dataset = self._data_panel.get_dataset()
        n_hl = len(dataset.homo_lumo)
        n_st = len(dataset.states)
        n_fc = len(dataset.franck_condon)
        self._show_status(
            f"Data modified \u2014 {n_hl} HOMO/LUMO entries, "
            f"{n_st} states, {n_fc} FC entries"
        )
        self._mark_dirty()

    def _on_tab_changed(self, idx: int) -> None:
        self._style_panel.set_active_tab(idx)
        self.refresh_active_diagram()

    def refresh_active_diagram(self) -> None:
        dataset = self._data_panel.get_dataset()
        style = self._style_panel.get_style()
        idx = self._tab_widget.currentIndex()
        logger.debug("refresh_active_diagram: tab=%d", idx)
        if idx == 0:
            self._homo_lumo_widget.refresh(dataset, style)
        elif idx == 1:
            self._state_diagram_widget.refresh(dataset, style)
        elif idx == 2:
            self._franck_condon_widget.refresh(dataset, style)

    # ------------------------------------------------------------------
    # Project state helpers
    # ------------------------------------------------------------------

    def get_ui_state(self) -> dict:
        return {
            "active_tab": self._tab_widget.currentIndex(),
            "fc_selected_compound": self._franck_condon_widget.get_selected_compound(),
            "fc_unit": self._franck_condon_widget.get_selected_unit(),
        }

    def apply_ui_state(self, ui_state: dict) -> None:
        tab = ui_state.get("active_tab", 0)
        if 0 <= tab < self._tab_widget.count():
            self._tab_widget.setCurrentIndex(tab)

    # ------------------------------------------------------------------
    # File menu actions
    # ------------------------------------------------------------------

    def _on_new_project(self) -> None:
        if self._dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Save changes before creating a new project?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if reply == QMessageBox.StandardButton.Save:
                if not self._save_project():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self._data_panel.set_dataset(DFTDataset.empty())
        self._style_panel.set_style(DEFAULT_STYLE)
        self._current_project_path = None
        self._mark_clean()
        self.refresh_active_diagram()
        self._show_status("New project created.")

    def _on_open_project(self) -> None:
        if self._dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Save changes before opening another project?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if reply == QMessageBox.StandardButton.Save:
                if not self._save_project():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        filepath_str, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", _PROJECT_FILTER
        )
        if not filepath_str:
            return
        filepath = Path(filepath_str)
        try:
            dataset, style, ui_state = load_project(filepath)
        except (ValueError, OSError, Exception) as exc:
            QMessageBox.critical(self, "Open Failed", f"Could not load project:\n{exc}")
            return

        self._data_panel.set_dataset(dataset)
        self._style_panel.set_style(style)
        self.apply_ui_state(ui_state)
        self._current_project_path = filepath
        self._mark_clean()
        self.refresh_active_diagram()
        self._show_status(f"Opened: {filepath.name}")

    def _on_save_project(self) -> None:
        self._save_project()

    def _on_save_project_as(self) -> None:
        self._save_project(force_dialog=True)

    def _save_project(self, force_dialog: bool = False) -> bool:
        """Save the current project. Returns True if saved, False if cancelled."""
        filepath = self._current_project_path
        if filepath is None or force_dialog:
            suggested = (
                str(filepath) if filepath else ""
            )
            filepath_str, _ = QFileDialog.getSaveFileName(
                self, "Save Project As", suggested, _PROJECT_FILTER
            )
            if not filepath_str:
                return False
            filepath = Path(filepath_str)
            if filepath.suffix.lower() != ".dftviz":
                filepath = filepath.with_suffix(".dftviz")

        try:
            dataset = self._data_panel.get_dataset()
            style = self._style_panel.get_style()
            ui_state = self.get_ui_state()
            save_project(filepath, dataset, style, ui_state)
        except OSError as exc:
            QMessageBox.critical(self, "Save Failed", f"Could not save project:\n{exc}")
            return False

        self._current_project_path = filepath
        self._mark_clean()
        self._show_status(f"Saved: {filepath.name}")
        return True

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _on_export_diagram(self) -> None:
        dlg = ExportDialog(self)
        if dlg.exec() != ExportDialog.DialogCode.Accepted:
            return

        scope = dlg.get_scope()
        fmt = dlg.get_format()
        dpi = dlg.get_dpi()
        figsize_cm = dlg.get_figsize_cm()
        background = dlg.get_background()
        tiff_compression = dlg.get_tiff_compression()
        output_folder = dlg.get_output_folder()
        filename = dlg.get_filename()

        try:
            if scope == "active":
                filepath = output_folder / f"{filename}.{fmt}"
                self._export_active_diagram(
                    filepath, dpi, fmt, figsize_cm, background, tiff_compression
                )
                exported = [filepath]
            else:
                exported = self._export_all_diagrams(
                    output_folder, filename, dpi, fmt, figsize_cm,
                    background, tiff_compression,
                )
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", f"Export error:\n{exc}")
            return

        # Success message with "Open folder" button
        paths_text = "\n".join(str(p) for p in exported)
        msg = QMessageBox(self)
        msg.setWindowTitle("Export Complete")
        msg.setText(f"Exported {len(exported)} file(s):")
        msg.setInformativeText(paths_text)
        msg.setIcon(QMessageBox.Icon.Information)
        open_btn = msg.addButton("Open Folder", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        if msg.clickedButton() == open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_folder)))

    def _export_active_diagram(
        self,
        filepath: Path,
        dpi: int,
        fmt: str,
        figsize_cm,
        background: str,
        tiff_compression: str,
    ) -> None:
        idx = self._tab_widget.currentIndex()
        widgets = [
            self._homo_lumo_widget,
            self._state_diagram_widget,
            self._franck_condon_widget,
        ]
        widgets[idx].export_figure(filepath, dpi, fmt, figsize_cm, background, tiff_compression)

    def _export_all_diagrams(
        self,
        base_path: Path,
        basename: str,
        dpi: int,
        fmt: str,
        figsize_cm,
        background: str,
        tiff_compression: str,
    ) -> list[Path]:
        suffixes = ["homo_lumo", "states", "franck_condon"]
        widgets = [
            self._homo_lumo_widget,
            self._state_diagram_widget,
            self._franck_condon_widget,
        ]
        exported = []
        for widget, suffix in zip(widgets, suffixes):
            filepath = base_path / f"{basename}_{suffix}.{fmt}"
            widget.export_figure(filepath, dpi, fmt, figsize_cm, background, tiff_compression)
            exported.append(filepath)
        return exported

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About DFT Visualizer",
            "DFT Visualizer v0.1.0\n\nPublication-quality DFT diagram tool.",
        )
