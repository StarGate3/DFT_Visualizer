"""Entry point for the DFT Visualizer application."""

import sys
import warnings

# Suppress a matplotlib shutdown artefact: during figure cleanup on exit,
# NavigationToolbar can trigger a redraw on a partially-destroyed axes whose
# x-scale has already been reset to 'log' by the Qt teardown sequence.
# This has no effect on rendering; suppressing it removes spurious console noise.
warnings.filterwarnings(
    "ignore",
    message="Attempt to set non-positive xlim on a log-scaled axis.*",
    category=UserWarning,
)

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
