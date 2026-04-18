# DFT Visualizer

A desktop application for visualizing Density Functional Theory (DFT) calculation results,
designed to produce publication-quality figures for peer-reviewed journals in computational
chemistry and photochemistry.

## Features

- **HOMO/LUMO diagrams** — horizontal energy levels with gap arrows and compound labels
- **S0/S1/T1 state diagrams** — electronic state energy levels with absorption and ISC annotations
- **Franck-Condon diagrams** — potential energy surfaces with vertical/adiabatic transitions and BDE annotations
- **Publication presets** — one-click settings for journal-ready figures (Arial 10pt, 300 DPI, etc.)
- **Colorblind-friendly and grayscale palettes**
- **Interactive label editing** — drag-and-drop repositioning, click-to-edit properties
- **Undo / Redo** (Ctrl+Z / Ctrl+Y)
- **Export** to PNG (300–1200 DPI) and TIFF (LZW compression, optional CMYK)

## Requirements

- Python 3.11 (via Conda)
- See `requirements.txt` for library versions

## Installation

```bash
conda create -n dft-viz python=3.11 -y
conda activate dft-viz
pip install -r requirements.txt
```

> **Windows note:** On systems with Anaconda/Miniconda, using a Conda environment avoids
> common DLL loading issues with PyQt6 that can occur when mixing venv with the Conda base
> environment.

## Usage

```bash
python main.py
```

## Project Structure

```
dft_visualizer/
├── main.py                      # Application entry point
├── requirements.txt
├── README.md
├── sample_compounds.xlsx        # Example data file
├── src/
│   ├── gui/
│   │   ├── main_window.py       # Main application window
│   │   ├── data_panel.py        # Data loading / editing panel
│   │   ├── style_panel.py       # Style & appearance panel
│   │   ├── export_panel.py      # Export dialog
│   │   └── diagram_widgets/     # Per-diagram Qt widgets
│   ├── data/
│   │   ├── models.py            # Dataclasses for HOMO/LUMO, States, Franck-Condon
│   │   ├── excel_parser.py      # Excel (.xlsx) parser
│   │   └── validator.py         # Input validation
│   ├── plotting/
│   │   ├── homo_lumo_plot.py
│   │   ├── state_plot.py
│   │   ├── franck_condon_plot.py
│   │   └── style_presets.py
│   └── export/
│       └── image_exporter.py
└── tests/
    ├── test_parser.py
    └── test_plotting.py
```

## Development Status

**Stage 1 of 6 — Skeleton only.**
The application window, menu bar, tab layout, and dock panels are in place.
No data loading, plotting, or style controls are implemented yet.

## License

MIT License (see LICENSE file)
