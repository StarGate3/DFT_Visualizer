"""Main application window for DFT Visualizer."""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QMenu,
    QStatusBar,
    QTabWidget,
    QWidget,
)

from src.gui.data_panel import DataPanel
from src.gui.diagram_widgets.franck_condon_diagram import FranckCondonDiagramWidget
from src.gui.diagram_widgets.homo_lumo_diagram import HomoLumoDiagramWidget
from src.gui.diagram_widgets.state_diagram import StateDiagramWidget
from src.gui.style_panel import StylePanel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Primary window of the DFT Visualizer application.

    Hosts the menu bar, a three-tab central diagram area, two dock panels
    (Data and Style & Appearance), and a status bar.
    """

    WINDOW_TITLE: str = "DFT Visualizer"
    DEFAULT_WIDTH: int = 1400
    DEFAULT_HEIGHT: int = 900
    MIN_WIDTH: int = 1000
    MIN_HEIGHT: int = 700

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the main window, building all UI components."""
        super().__init__(parent)
        self._setup_window()
        self._build_menu_bar()
        self._build_central_widget()
        self._build_dock_widgets()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        """Configure window geometry, title, and icon."""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        # TODO: replace QIcon() with an actual application icon asset
        self.setWindowIcon(QIcon())

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------

    def _build_menu_bar(self) -> None:
        """Construct the full menu bar with all menus and actions."""
        menu_bar = self.menuBar()
        assert menu_bar is not None

        self._build_file_menu(menu_bar)
        self._build_edit_menu(menu_bar)
        self._build_view_menu(menu_bar)
        self._build_export_menu(menu_bar)
        self._build_help_menu(menu_bar)

    def _build_file_menu(self, menu_bar: object) -> None:
        """Create the File menu with project and import actions."""
        file_menu: QMenu = menu_bar.addMenu("&File")  # type: ignore[attr-defined]

        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(lambda: self._stub("new_project"))
        file_menu.addAction(new_action)

        open_action = QAction("&Open Project…", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(lambda: self._stub("open_project"))
        file_menu.addAction(open_action)

        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(lambda: self._stub("save_project"))
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Project &As…", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(lambda: self._stub("save_project_as"))
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        import_action = QAction("&Import Excel…", self)
        import_action.setShortcut("Ctrl+I")
        # Connection deferred to _build_dock_widgets once DataPanel is created.
        self._import_action = import_action
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _build_edit_menu(self, menu_bar: object) -> None:
        """Create the Edit menu. Undo/Redo are disabled pending Command pattern implementation."""
        edit_menu: QMenu = menu_bar.addMenu("&Edit")  # type: ignore[attr-defined]

        # TODO: enable once Command pattern (undo/redo stack) is implemented
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False)
        undo_action.triggered.connect(lambda: self._stub("undo"))
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setEnabled(False)
        redo_action.triggered.connect(lambda: self._stub("redo"))
        edit_menu.addAction(redo_action)

        self._undo_action = undo_action
        self._redo_action = redo_action

    def _build_view_menu(self, menu_bar: object) -> None:
        """Create the View menu with dock panel toggles.

        Stored as instance attributes so the dock widgets can be referenced
        once they are created in _build_dock_widgets.
        """
        view_menu: QMenu = menu_bar.addMenu("&View")  # type: ignore[attr-defined]

        self._toggle_data_action = QAction("Toggle &Data Panel", self)
        self._toggle_data_action.setCheckable(True)
        self._toggle_data_action.setChecked(True)
        view_menu.addAction(self._toggle_data_action)

        self._toggle_style_action = QAction("Toggle &Style Panel", self)
        self._toggle_style_action.setCheckable(True)
        self._toggle_style_action.setChecked(True)
        view_menu.addAction(self._toggle_style_action)

    def _build_export_menu(self, menu_bar: object) -> None:
        """Create the Export menu. Actions disabled until plotting is implemented."""
        export_menu: QMenu = menu_bar.addMenu("E&xport")  # type: ignore[attr-defined]

        # TODO: enable once plotting and export pipeline are implemented
        png_action = QAction("Export as &PNG…", self)
        png_action.setEnabled(False)
        png_action.triggered.connect(lambda: self._stub("export_png"))
        export_menu.addAction(png_action)

        tiff_action = QAction("Export as &TIFF…", self)
        tiff_action.setEnabled(False)
        tiff_action.triggered.connect(lambda: self._stub("export_tiff"))
        export_menu.addAction(tiff_action)

    def _build_help_menu(self, menu_bar: object) -> None:
        """Create the Help menu."""
        help_menu: QMenu = menu_bar.addMenu("&Help")  # type: ignore[attr-defined]

        about_action = QAction("&About", self)
        about_action.triggered.connect(lambda: self._stub("about"))
        help_menu.addAction(about_action)

        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(lambda: self._stub("documentation"))
        help_menu.addAction(docs_action)

    # ------------------------------------------------------------------
    # Central widget (tab area)
    # ------------------------------------------------------------------

    def _build_central_widget(self) -> None:
        """Create the three-tab central diagram area.

        Tab 0 hosts the live HomoLumoDiagramWidget.
        Tab 1 hosts the live StateDiagramWidget.
        Tab 2 remains a placeholder until Stage 5.
        """
        self._tab_widget = QTabWidget(self)
        self.setCentralWidget(self._tab_widget)

        self._homo_lumo_widget = HomoLumoDiagramWidget(self)
        self._tab_widget.addTab(self._homo_lumo_widget, "HOMO/LUMO")

        self._state_diagram_widget = StateDiagramWidget(self)
        self._tab_widget.addTab(self._state_diagram_widget, "S0/S1/T1 States")

        self._franck_condon_widget = FranckCondonDiagramWidget(self)
        self._tab_widget.addTab(self._franck_condon_widget, "Franck-Condon")

    def _make_placeholder_label(self, text: str) -> QLabel:
        """Return a centered, styled placeholder QLabel for an empty tab."""
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
        """Create the Data and Style dock widgets and wire them to View menu toggles."""
        allowed_areas = (
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Data dock — left side
        self._data_dock = QDockWidget("Data", self)
        self._data_dock.setAllowedAreas(allowed_areas)
        self._data_panel = DataPanel(self)
        self._data_dock.setWidget(self._data_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._data_dock)

        # Wire up Import Excel menu action now that DataPanel exists.
        self._import_action.triggered.connect(self._data_panel.load_from_excel)

        # Status bar updates from DataPanel signals.
        self._data_panel.status_message.connect(self._show_status)
        self._data_panel.data_changed.connect(self._on_data_changed)

        # Style dock — right side
        self._style_dock = QDockWidget("Style & Appearance", self)
        self._style_dock.setAllowedAreas(allowed_areas)
        self._style_panel = StylePanel(self)
        self._style_dock.setWidget(self._style_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._style_dock)

        # Diagram refresh connections
        self._data_panel.data_changed.connect(self.refresh_active_diagram)
        self._data_panel.dataset_loaded.connect(self.refresh_active_diagram)
        self._style_panel.style_changed.connect(self.refresh_active_diagram)
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

        # Wire View menu toggles
        self._toggle_data_action.toggled.connect(self._data_dock.setVisible)
        self._toggle_style_action.toggled.connect(self._style_dock.setVisible)

        # Keep menu checkboxes in sync when user closes docks via the 'X' button
        self._data_dock.visibilityChanged.connect(self._toggle_data_action.setChecked)
        self._style_dock.visibilityChanged.connect(self._toggle_style_action.setChecked)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _build_status_bar(self) -> None:
        """Create and configure the status bar."""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")

    # ------------------------------------------------------------------
    # Status bar helpers
    # ------------------------------------------------------------------

    def _show_status(self, message: str) -> None:
        """Display *message* on the status bar."""
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(message)

    def _on_data_changed(self) -> None:
        """Update status bar with current row counts whenever data is edited."""
        dataset = self._data_panel.get_dataset()
        n_hl = len(dataset.homo_lumo)
        n_st = len(dataset.states)
        n_fc = len(dataset.franck_condon)
        self._show_status(
            f"Data modified \u2014 {n_hl} HOMO/LUMO entries, "
            f"{n_st} states, {n_fc} FC entries"
        )

    def _on_tab_changed(self, idx: int) -> None:
        """Handle tab change: update style panel sections and refresh diagram."""
        self._style_panel.set_active_tab(idx)
        self.refresh_active_diagram()

    def refresh_active_diagram(self) -> None:
        """Re-render whichever diagram tab is currently visible.

        Fetches the current dataset and style, then calls refresh() on the
        appropriate diagram widget.  Tab 2 is a placeholder and does
        nothing until Stage 5.
        """
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
    # Stub handler
    # ------------------------------------------------------------------

    def _stub(self, action_name: str) -> None:
        """Print a placeholder message for unimplemented menu actions."""
        print(f"TODO: Implement {action_name}")
