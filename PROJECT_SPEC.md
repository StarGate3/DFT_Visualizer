# DFT Visualizer - Specyfikacja Projektu

## 1. Cel aplikacji

Aplikacja desktopowa do wizualizacji wyników obliczeń DFT (Density Functional Theory) z przeznaczeniem do przygotowywania grafik do recenzowanych publikacji naukowych w chemii kwantowej i fotochemii.

## 2. Użytkownik docelowy

Naukowcy zajmujący się chemią obliczeniową, fotochemią, spektroskopią molekularną. Użytkownik pracuje z wynikami z programów typu Gaussian, ORCA, Q-Chem, Turbomole. Potrzebuje szybko generować wysokiej jakości diagramy energii molekularnych.

## 3. Stack technologiczny

- **Python 3.10+**
- **PyQt6** - framework GUI
- **matplotlib 3.8+** - renderowanie diagramów
- **pandas 2.0+** - obsługa danych tabelarycznych
- **openpyxl** - parsowanie plików Excel (.xlsx)
- **numpy** - obliczenia numeryczne
- **scipy** - funkcje matematyczne (krzywe Morse'a dla Franck-Condon)

## 4. Struktura projektu

```
dft_visualizer/
├── main.py                          # Punkt wejściowy aplikacji
├── requirements.txt                 # Zależności Python
├── README.md                        # Dokumentacja
├── PROJECT_SPEC.md                  # Ten dokument
├── sample_data/                     # Przykładowe pliki danych
│   └── sample_compounds.xlsx
├── src/
│   ├── __init__.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py           # Główne okno aplikacji
│   │   ├── data_panel.py            # Panel wczytywania/edycji danych
│   │   ├── style_panel.py           # Panel personalizacji wyglądu
│   │   ├── export_panel.py          # Panel eksportu
│   │   └── diagram_widgets/
│   │       ├── __init__.py
│   │       ├── base_diagram.py      # Klasa bazowa diagramu
│   │       ├── homo_lumo_diagram.py # Diagram HOMO/LUMO
│   │       ├── state_diagram.py     # Diagram S0/S1/T1
│   │       └── franck_condon.py     # Diagram Franck-Condon
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models.py                # Modele danych (dataclasses)
│   │   ├── excel_parser.py          # Parser Excel
│   │   └── validator.py             # Walidacja danych
│   ├── plotting/
│   │   ├── __init__.py
│   │   ├── homo_lumo_plot.py        # Logika rysowania HOMO/LUMO
│   │   ├── state_plot.py            # Logika rysowania S0/S1/T1
│   │   ├── franck_condon_plot.py    # Logika Franck-Condon
│   │   └── style_presets.py         # Presety kolorystyczne
│   └── export/
│       ├── __init__.py
│       └── image_exporter.py        # Eksport PNG/TIFF
└── tests/
    ├── __init__.py
    ├── test_parser.py
    └── test_plotting.py
```

## 5. Format danych wejściowych (Excel)

Plik Excel powinien mieć trzy arkusze (tabs):

### Arkusz 1: "HOMO_LUMO"
| compound_name | HOMO_eV | LUMO_eV |
|---------------|---------|---------|
| Benzofenon    | -7.16   | -2.17   |
| 55-023        | -6.70   | -2.30   |

Gap jest **obliczany automatycznie** jako `LUMO - HOMO`.

### Arkusz 2: "States"
| compound_name | S0_eV | S1_eV | T1_eV |
|---------------|-------|-------|-------|
| PK08-038      | 0.00  | 3.22  | 2.31  |
| PK05-001      | 0.00  | 2.64  | 2.45  |

### Arkusz 3: "FranckCondon" (opcjonalnie)
| compound_name | state | E_vertical | E_adiabatic | BDE_value | BDE_label |
|---------------|-------|------------|-------------|-----------|-----------|
| Compound_A    | S1    | 73.3       | 69.8        | 3.8       | S1_ver-C14-Br |
| Compound_A    | T1    | 50.0       | 43.7        |           |               |
| Compound_A    | S0    | 0.0        | 0.0         | 77.1      | S0-C5-Br      |

## 6. Funkcjonalności szczegółowe

### 6.1 Diagram HOMO/LUMO
- Poziome czerwone linie dla HOMO, niebieskie dla LUMO (konfigurowalne)
- Wartości energii wyświetlane nad/pod każdą linią
- Strzałka dwukierunkowa między HOMO a LUMO z wartością gap
- Etykiety związków pod diagramem
- Automatyczne skalowanie osi Y
- Możliwość wyświetlania wielu związków obok siebie

### 6.2 Diagram stanów S0/S1/T1
- Poziome linie: S0 (granatowa), S1 (ciemnoczerwona), T1 (zielona) - konfigurowalne
- Strzałka pionowa z podpisem "Abs." od S0 do S1 (absorpcja)
- Krzywa przerywana z podpisem "ISC" od S1 do T1 (Intersystem Crossing)
- Wartości energii nad poziomami
- Etykiety S0, S1, T1 przy liniach
- Oś Y: Energia (eV), z reguły 0 to S0, ale możliwość przesunięcia

### 6.3 Diagram Franck-Condon
- Trzy krzywe potencjalne (S0, S1, T1) w postaci funkcji Morse'a lub parabol
- Strzałka pionowa (linia ciągła) dla przejścia wertykalnego Franck-Condon
- Strzałka przerywana dla przejścia adiabatycznego
- Linie pomocnicze (przerywane) dla E_vertical i E_adiabatic
- Wartości BDE (Bond Dissociation Energy) z etykietami i strzałkami z boku
- Podpisy S_0, S_1, T_1 przy krzywych
- Oś Y: Energia (kcal/mol lub eV - wybór użytkownika)
- Oś X: Współrzędna reakcji (bezwymiarowa)

### 6.4 Personalizacja (Style Panel)
- **Czcionki**: wybór rodziny (Arial, Times New Roman, Helvetica, DejaVu Sans, Computer Modern)
- **Rozmiary**: osobne dla tytułu, etykiet osi, wartości, legend
- **Kolory**: color pickery dla każdego elementu
- **Grubość linii**: suwaki
- **Style strzałek**: typ grota, szerokość
- **Tło**: białe / przezroczyste
- **Siatka**: włącz/wyłącz, kolor, styl
- **Granice osi**: automatyczne lub ręczne (min/max)
- **Preset "Publication"**: jednym kliknięciem ustawia optymalne parametry dla publikacji (Arial 10pt, linie 1.5pt, DPI 300, itp.)
- **Preset "Colorblind-friendly"**: paleta przyjazna dla daltonistów
- **Preset "Grayscale"**: czarno-biały do czasopism drukowanych

### 6.5 Interaktywna edycja
- **Drag & drop** etykiet energii (korekta pozycji tekstu gdy nachodzi na linię)
- **Klik na element** → otwiera dialog edycji właściwości
- **Klik prawym** → menu kontekstowe (usuń, duplikuj, edytuj)
- **Undo/Redo** (Ctrl+Z / Ctrl+Y)

### 6.6 Eksport
- **PNG**: 300, 600, 1200 DPI
- **TIFF**: z kompresją LZW, 300+ DPI, tryb CMYK opcjonalnie
- **Rozmiary**: preset "single column" (3.5"), "double column" (7"), "custom"
- **Tło**: białe lub przezroczyste
- Podgląd przed eksportem

## 7. Standardy publikacyjne (do respektowania)

Aplikacja powinna domyślnie generować grafiki zgodne z wymogami głównych czasopism chemicznych:
- **Rozdzielczość**: minimum 300 DPI dla rastrów
- **Czcionki**: bezszeryfowe (Arial, Helvetica) rozmiar 8-12pt
- **Linie**: grubość 0.75-1.5pt
- **Kolor**: CMYK-compatible lub grayscale
- **Szerokość**: single column ≈ 3.5" (89mm), double column ≈ 7.3" (183mm)

## 8. Architektura - wzorce projektowe

- **MVC**: model danych oddzielony od widoku (GUI) i kontrolera (logika)
- **Observer pattern**: zmiany w panelu personalizacji od razu odświeżają podgląd
- **Strategy pattern**: różne typy diagramów dzielą wspólny interfejs
- **Command pattern**: dla systemu Undo/Redo

## 9. Obsługa błędów

- Walidacja danych z czytelnymi komunikatami
- Try/except wokół operacji I/O (otwarcie pliku, zapis)
- Komunikaty ostrzegawcze w GUI (QMessageBox)
- Logowanie błędów do pliku `dft_visualizer.log`

## 10. Wydajność

- Renderowanie w tle (QThread) dla złożonych diagramów
- Cache dla obliczeń krzywych Morse'a
- Debouncing zmian w panelu stylów (aktualizacja co 200ms)

## 11. Docelowy rozmiar kodu

- Łącznie ~3000-5000 linii Python
- Każdy moduł < 500 linii (zasada pojedynczej odpowiedzialności)
- Pokrycie testami: przynajmniej moduły parsowania i obliczeń
