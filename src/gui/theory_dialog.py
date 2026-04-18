"""Theory dialog — wyświetla merytoryczne wyjaśnienia diagramów DFT.

Okno ma dwa panele:
- Lewy: lista sekcji (QListWidget) do nawigacji
- Prawy: obszar tekstowy (QTextBrowser) z bogatym HTML

Wybór sekcji z lewej strony aktualizuje treść po prawej. Okno
nie jest modalne — można go zostawić otwarte obok głównej aplikacji
podczas analizy diagramów.
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
    """Niemodalne okno z teorią diagramów DFT.

    Okno pamięta ostatnio oglądaną sekcję pomiędzy otwarciami
    (zmienna klasowa _last_section). Otwiera się domyślnie z rozmiarem
    900x650 ale jest w pełni skalowalne.
    """

    # Zapamiętuje ostatnio wybraną sekcję między otwarciami okna
    _last_section: str = "overview"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Teoria diagramów — DFT Visualizer")
        self.resize(900, 650)
        self.setMinimumSize(QSize(650, 400))

        # Niemodalne okno — użytkownik może wrócić do głównej aplikacji
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

        # Górny wiersz: dwa panele obok siebie
        content_row = QHBoxLayout()
        content_row.setSpacing(10)

        # Lewy panel — lista sekcji
        self._section_list = QListWidget()
        self._section_list.setFixedWidth(220)
        self._section_list.setFont(QFont("", 10))
        self._section_list.currentItemChanged.connect(self._on_section_selected)
        content_row.addWidget(self._section_list)

        # Prawy panel — treść HTML
        self._content_view = QTextBrowser()
        self._content_view.setOpenExternalLinks(True)
        # Preferred internal font for readability
        content_font = QFont("Arial", 11)
        self._content_view.setFont(content_font)
        # Trochę marginesu w środku dla wygody czytania
        self._content_view.document().setDocumentMargin(12)
        content_row.addWidget(self._content_view, 1)

        main_layout.addLayout(content_row, 1)

        # Dolny pasek z przyciskiem zamknięcia
        button_row = QHBoxLayout()
        button_row.addStretch(1)

        close_btn = QPushButton("Zamknij")
        close_btn.setFixedWidth(100)
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.close)
        button_row.addWidget(close_btn)

        main_layout.addLayout(button_row)

    # ------------------------------------------------------------------
    # Populating & navigation
    # ------------------------------------------------------------------

    def _populate_sections(self) -> None:
        """Wypełnia listę sekcji na podstawie THEORY_SECTIONS."""
        for key, (display_name, _html) in THEORY_SECTIONS.items():
            item = QListWidgetItem(display_name)
            # Przechowujemy klucz sekcji w Qt.ItemDataRole.UserRole
            item.setData(Qt.ItemDataRole.UserRole, key)
            self._section_list.addItem(item)

    def _restore_last_section(self) -> None:
        """Ustawia sekcję zapamiętaną z poprzedniego otwarcia okna."""
        target_key = TheoryDialog._last_section
        for i in range(self._section_list.count()):
            item = self._section_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == target_key:
                self._section_list.setCurrentRow(i)
                return
        # Fallback: pierwszy element
        if self._section_list.count() > 0:
            self._section_list.setCurrentRow(0)

    def _on_section_selected(
        self,
        current: Optional[QListWidgetItem],
        previous: Optional[QListWidgetItem],  # noqa: ARG002 — unused but required by signal
    ) -> None:
        """Ładuje HTML dla wybranej sekcji do prawego panelu."""
        if current is None:
            return
        key = current.data(Qt.ItemDataRole.UserRole)
        if key in THEORY_SECTIONS:
            _display_name, html = THEORY_SECTIONS[key]
            self._content_view.setHtml(html)
            # Zapamiętaj wybór dla następnego otwarcia
            TheoryDialog._last_section = key
