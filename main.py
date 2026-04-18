"""Entry point for the DFT Visualizer application."""

import sys

from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def main() -> None:
    """Initialize and launch the DFT Visualizer application."""
    app = QApplication(sys.argv)
    app.setApplicationName("DFT Visualizer")
    app.setOrganizationName("Computational Chemistry Lab")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
