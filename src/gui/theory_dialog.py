"""Theory dialog — displays theoretical explanations of DFT diagrams.

The window has two panels:
- Left: section list (QListWidget) for navigation
- Right: text area (QTextBrowser) with rich HTML

Selecting a section on the left updates the content on the right.
The window is non-modal — the user can keep it open next to the main
application while analyzing diagrams.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.gui.theory_content import THEORY_SECTIONS


class TheoryDialog(QDialog):
    """Non-modal window with theoretical background for DFT diagrams.

    The window remembers the last-viewed section between openings
    (class-level _last_section variable). Default size 900x650 but
    fully resizable.
    """

    # Remembers the last-selected section between window openings
    _last_section: str = "overview"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Theory — DFT Visualizer")
        self.resize(900, 650)
        self.setMinimumSize(QSize(650, 400))

        # Non-modal — user can return to the main application
        self.setModal(False)

        self._setup_ui()
        self._populate_sections()
        self._restore_last_section()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Top row: two panels side by side
        content_row = QHBoxLayout()
        content_row.setSpacing(10)

        # Left panel — section list
        self._section_list = QListWidget()
        self._section_list.setFixedWidth(220)
        self._section_list.setFont(QFont("", 10))
        self._section_list.currentItemChanged.connect(self._on_section_selected)
        content_row.addWidget(self._section_list)

        # Right panel — HTML content
        self._content_view = QTextBrowser()
        self._content_view.setOpenExternalLinks(True)
        # Preferred internal font for readability
        content_font = QFont("Arial", 11)
        self._content_view.setFont(content_font)
        # Small internal margin for comfortable reading
        self._content_view.document().setDocumentMargin(12)
        content_row.addWidget(self._content_view, 1)

        main_layout.addLayout(content_row, 1)

        # Bottom bar with Close button
        button_row = QHBoxLayout()
        button_row.addStretch(1)

        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.close)
        button_row.addWidget(close_btn)

        main_layout.addLayout(button_row)

    # ------------------------------------------------------------------
    # Populating & navigation
    # ------------------------------------------------------------------

    def _populate_sections(self) -> None:
        """Populate the section list from THEORY_SECTIONS."""
        for key, (display_name, _html) in THEORY_SECTIONS.items():
            item = QListWidgetItem(display_name)
            # Store the section key in Qt.ItemDataRole.UserRole
            item.setData(Qt.ItemDataRole.UserRole, key)
            self._section_list.addItem(item)

    def _restore_last_section(self) -> None:
        """Select the section remembered from the previous opening."""
        target_key = TheoryDialog._last_section
        for i in range(self._section_list.count()):
            item = self._section_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == target_key:
                self._section_list.setCurrentRow(i)
                return
        # Fallback: first entry
        if self._section_list.count() > 0:
            self._section_list.setCurrentRow(0)

    def _on_section_selected(
        self,
        current: Optional[QListWidgetItem],
        previous: Optional[QListWidgetItem],  # noqa: ARG002 — unused but required by signal
    ) -> None:
        """Load HTML for the selected section into the right panel."""
        if current is None:
            return
        key = current.data(Qt.ItemDataRole.UserRole)
        if key in THEORY_SECTIONS:
            _display_name, html = THEORY_SECTIONS[key]
            self._content_view.setHtml(html)
            # Remember this selection for next opening
            TheoryDialog._last_section = key