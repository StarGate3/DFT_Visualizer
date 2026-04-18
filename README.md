# DFT Visualizer

**Publication-quality visualization tool for Density Functional Theory (DFT) and TD-DFT computational chemistry results.**

A desktop application that converts numerical outputs from quantum chemistry packages (Gaussian, ORCA, Q-Chem, etc.) into three types of publication-ready diagrams:

- 🔴 **HOMO/LUMO energy diagrams** — frontier molecular orbital energies
- 🟢 **Electronic state diagrams (S₀/S₁/T₁)** — singlet/triplet states with absorption and intersystem crossing
- 🟠 **Franck-Condon schematic diagrams** — potential energy surfaces with vertical/adiabatic transitions

Built with PyQt6 and matplotlib. Exports to PNG, TIFF, SVG, and PDF at resolutions from 300 DPI up to 1200 DPI.

---

## ✨ Features

### Three scientific diagram types
- **HOMO/LUMO diagram** with configurable gap arrows, value formats, and label offsets
- **S₀/S₁/T₁ state diagram** with absorption arrows, ISC pathways, and per-state styling
- **Franck-Condon schematic** with Morse-like potential wells, vibrational levels, and wavefunction indicators

### Full style customization
- Five built-in presets: **Default**, **Publication**, **Publication High-DPI**, **Colorblind-safe**, **Grayscale**
- Per-diagram controls for colors, line widths, fonts, offsets
- Publication-safe fonts (Arial, Helvetica, Times New Roman, Computer Modern Roman)
- Dynamic style panel that adapts to the active diagram tab

### Interactive UX
- **Drag-and-drop labels** — reposition any text label by mouse
- **Draggable arrows** — move absorption and ISC arrows horizontally
- **Right-click context menus** — edit text, change colors, line widths, line styles in-place
- **Undo/Redo** — 50-step history (Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z)
- **Keyboard shortcuts** — Ctrl+1/2/3 switches diagram tabs, F1 for help, Ctrl+E for export

### Publication export
- **Formats**: PNG, TIFF (with LZW/Deflate compression), SVG, PDF
- **Resolution**: 300/600/1200 DPI plus custom
- **Figure sizes**: Nature single/double column, JACS single/double, A4, Letter, Square, Custom
- **Background**: transparent, white, or style-matched
- **Batch export**: save all three diagrams at once

### Project save/load
- Full app state serialization to `.dftviz` (JSON format)
- Preserves data, styling, label positions, FC compound selection, and UI state
- Dirty-flag prompt on close

### Built-in theory reference
- In-app **Theory** window explaining the physics behind each diagram type
- Polish-language content aimed at master's/PhD students
- Covers HOMO/LUMO, electronic states, Franck-Condon principle, and DFT/TD-DFT methodology

---

## 📸 Screenshots

*(Add screenshots of your three diagrams here after first release. Suggested: one hero shot of each diagram + one of the full app window.)*

---

## 🚀 Installation

### Requirements
- Python 3.10 or newer
- Windows, macOS, or Linux

### Setup

**Option 1: with conda (recommended)**

```bash
git clone https://github.com/StarGate3/DFT_Visualizer.git
cd DFT_Visualizer
conda create -n dft-viz python=3.11
conda activate dft-viz
pip install -r requirements.txt
```

**Option 2: with venv**

```bash
git clone https://github.com/StarGate3/DFT_Visualizer.git
cd DFT_Visualizer
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

---

## 📖 Quick Start

1. **Launch** the application: `python main.py`
2. **Import data**: `File → Import Excel...` (or drop an .xlsx file)
3. **Try** `sample_compounds.xlsx` included in the repo
4. **Navigate** between diagrams with **Ctrl+1**, **Ctrl+2**, **Ctrl+3**
5. **Customize** via the right-side Style panel, or apply a preset
6. **Reposition** any label by dragging it with the mouse
7. **Export** the active diagram (or all three): `File → Export Diagram...` (**Ctrl+E**)
8. **Save** your project for later: `File → Save Project As...` (**Ctrl+Shift+S**) → generates a `.dftviz` file

For theoretical background on each diagram type, open **Help → Theory** (in Polish).

---

## 📋 Data Format

Input is an Excel file (`.xlsx`) with up to three sheets. Each sheet is independent — you can have just HOMO/LUMO data, just states, or all three.

### Sheet: `HOMO_LUMO`
| Column | Type | Description |
|--------|------|-------------|
| Compound | text | Molecule name |
| HOMO | number | HOMO energy in eV (typically negative) |
| LUMO | number | LUMO energy in eV |

### Sheet: `States`
| Column | Type | Description |
|--------|------|-------------|
| Compound | text | Molecule name |
| S0 | number | Ground state energy in eV (typically 0.0) |
| T1 | number | First triplet excited state in eV |
| S1 | number | First singlet excited state in eV |

### Sheet: `FranckCondon`
| Column | Type | Description |
|--------|------|-------------|
| Compound | text | Molecule name |
| State | text | `S0`, `S1`, or `T1` |
| E_vertical | number | Vertical excitation energy (kcal/mol) |
| E_adiabatic | number | Adiabatic excitation energy (kcal/mol) |
| BDE_value | number | *(optional, currently ignored)* |
| BDE_label | text | *(optional, currently ignored)* |

Multiple rows per compound are supported — the same state can appear in multiple rows with different BDE annotations.

A working example file (`sample_compounds.xlsx`) is included in the repository.

---

## 🛠️ How the Data Is Generated

Typical workflow to produce the input values:

1. **Geometry optimization** of the molecule in S₀ (any DFT functional, e.g., B3LYP/6-31G(d,p))
2. **Frequency calculation** to confirm the minimum (no imaginary frequencies)
3. **TD-DFT single-point** at S₀ geometry → gives **vertical** S₁ and T₁ energies
4. **TD-DFT optimization** of S₁ and T₁ → gives **adiabatic** energies
5. **Read HOMO/LUMO** directly from the S₀ ground-state DFT calculation output

Recommended functionals:
- **B3LYP** or **PBE0** — generic organic molecules
- **CAM-B3LYP** — charge-transfer states
- **ωB97X-D** — general-purpose choice with dispersion correction

---

## 🧪 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New project |
| `Ctrl+O` | Open project (`.dftviz`) |
| `Ctrl+S` | Save project |
| `Ctrl+Shift+S` | Save project as... |
| `Ctrl+E` | Export diagram(s) |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo |
| `Ctrl+1` / `Ctrl+2` / `Ctrl+3` | Switch to HOMO-LUMO / States / Franck-Condon |
| `F1` | Help → About |

Right-click on any diagram element for context menu actions.

---

## 🏗️ Architecture

```
dft_visualizer/
├── main.py                     # Entry point
├── requirements.txt
├── sample_compounds.xlsx       # Example data
├── src/
│   ├── gui/
│   │   ├── main_window.py         # Main window, menu, file I/O
│   │   ├── data_panel.py          # Editable data tables
│   │   ├── style_panel.py         # Dynamic style controls (QStackedWidget)
│   │   ├── export_dialog.py       # Export settings dialog
│   │   ├── history_manager.py     # Undo/redo
│   │   ├── theory_dialog.py       # In-app theory reference
│   │   ├── theory_content.py      # Theory HTML content (Polish)
│   │   └── diagram_widgets/
│   │       ├── base_diagram.py        # Context menu logic, shared behavior
│   │       ├── draggable.py           # DraggableText + DraggableArrow managers
│   │       ├── homo_lumo_diagram.py
│   │       ├── state_diagram.py
│   │       └── franck_condon_diagram.py
│   ├── data/
│   │   ├── models.py              # Dataclasses for compounds
│   │   ├── excel_parser.py
│   │   ├── validator.py
│   │   └── project_io.py          # .dftviz save/load
│   └── plotting/
│       ├── homo_lumo_plot.py
│       ├── state_plot.py
│       ├── franck_condon_plot.py  # Fixed-template schematic
│       ├── style_presets.py       # 5 presets + TypedDicts
│       └── plot_helpers.py
```

---

## 📜 License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for full terms.

**In short:** free to use, modify, and distribute for any purpose — academic or commercial — as long as you keep the copyright notice.

---

## 👤 Author

**StarGate3**
GitHub: [@StarGate3](https://github.com/StarGate3)
Repository: [DFT_Visualizer](https://github.com/StarGate3/DFT_Visualizer)

---

## 🙏 Acknowledgments

- Built with [PyQt6](https://riverbankcomputing.com/software/pyqt/) and [matplotlib](https://matplotlib.org/)
- Inspired by diagram conventions commonly used in photochemistry and photophysics literature
- Color palettes: [Okabe-Ito](https://jfly.uni-koeln.de/color/) (colorblind-safe)

---

## 📚 Citation

If this tool contributed to a publication, a citation would be appreciated:

```
DFT Visualizer. StarGate3, 2026.
https://github.com/StarGate3/DFT_Visualizer
```

---

## 🐛 Issues and Contributions

Found a bug or want to suggest a feature? [Open an issue](https://github.com/StarGate3/DFT_Visualizer/issues).

Pull requests are welcome.
