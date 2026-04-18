"""Merytoryczna zawartość okna 'Theory' (polski, średni poziom szczegółowości).

Treść skierowana do studentów magisterskich / doktorantów pierwszego roku
pracujących z obliczeniami DFT/TD-DFT. Cel: czytelnik po 5 minutach
rozumie co przedstawia każdy z trzech diagramów i dlaczego dany element
wygląda tak, a nie inaczej.

Używamy HTML z matplotlib-style MathJax/LaTeX (Qt rich text text obsługuje
prosty HTML + subset CSS).
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Sekcja 1: HOMO/LUMO
# ---------------------------------------------------------------------------

HOMO_LUMO_HTML = """
<h2>🔴 Diagram HOMO/LUMO</h2>

<h3>Co przedstawia diagram?</h3>
<p>
Diagram <b>HOMO/LUMO</b> pokazuje energie dwóch najważniejszych orbitali
molekularnych:
</p>
<ul>
  <li><b>HOMO</b> (<i>Highest Occupied Molecular Orbital</i>) — najwyższy
      obsadzony orbital molekularny. To "szczyt" zapełnionej części
      struktury elektronowej cząsteczki.</li>
  <li><b>LUMO</b> (<i>Lowest Unoccupied Molecular Orbital</i>) — najniższy
      nieobsadzony orbital molekularny. To pierwszy "wolny" orbital
      do którego może być wzbudzony elektron.</li>
</ul>

<h3>Dlaczego te dwa orbitale są ważne?</h3>
<p>
HOMO i LUMO definiują <b>reaktywność chemiczną</b> cząsteczki:
</p>
<ul>
  <li>Energia HOMO jest miarą zdolności do <b>oddawania elektronów</b>
      (potencjał jonizacji, ~IP). Wyższe HOMO = łatwiejsze utlenianie.</li>
  <li>Energia LUMO opisuje zdolność do <b>przyjmowania elektronów</b>
      (powinowactwo elektronowe, ~EA). Niższe LUMO = łatwiejsza redukcja.</li>
  <li><b>Różnica energii LUMO − HOMO</b>, zwana <b>przerwą HOMO/LUMO</b>
      (<i>gap</i>), jest pierwszym przybliżeniem energii przejścia
      elektronowego i optycznego.</li>
</ul>

<h3>Elementy diagramu</h3>
<ul>
  <li><b>Czerwone linie poziome</b> — poziomy HOMO dla każdej cząsteczki
      (kolor konfigurowalny).</li>
  <li><b>Niebieskie linie poziome</b> — poziomy LUMO.</li>
  <li><b>Pionowa strzałka z wartością</b> — wielkość przerwy HOMO/LUMO,
      zwykle w eV.</li>
  <li><b>Wartości liczbowe obok linii</b> — energie orbitali w eV
      (wartości ujemne, bo energia odnosi się do poziomu próżni).</li>
</ul>

<h3>Interpretacja praktyczna</h3>
<p>
Cząsteczki o <b>małej przerwie HOMO/LUMO</b> są na ogół:
</p>
<ul>
  <li>Bardziej reaktywne fotochemicznie.</li>
  <li>Absorbują światło o dłuższych falach (przesunięcie batochromowe).</li>
  <li>Częściej używane jako chromofory/barwniki organiczne.</li>
</ul>
<p>
Cząsteczki o <b>dużej przerwie</b> są zwykle stabilne, bezbarwne
i mniej reaktywne.
</p>

<h3>⚠️ Uwaga metodologiczna</h3>
<p>
Energia HOMO i LUMO obliczona metodą <b>DFT</b> (np. B3LYP) jest
<b>tylko przybliżeniem</b> prawdziwych energii orbitali Kohna-Shama.
Dokładne wartości IP i EA wymagają osobnych obliczeń (Δ-SCF lub
metody Greena). Przerwa HOMO/LUMO w DFT zwykle zaniża rzeczywistą
przerwę optyczną o 30–50%.
</p>
"""


# ---------------------------------------------------------------------------
# Sekcja 2: Stany elektronowe S0/S1/T1
# ---------------------------------------------------------------------------

STATES_HTML = """
<h2>🟢 Diagram stanów elektronowych S₀/S₁/T₁</h2>

<h3>Co przedstawia diagram?</h3>
<p>
Ten diagram pokazuje <b>energie stanów elektronowych</b> cząsteczki,
obliczone zwykle metodą <b>TD-DFT</b> (<i>Time-Dependent Density
Functional Theory</i>):
</p>
<ul>
  <li><b>S₀</b> — <b>stan podstawowy singletowy</b> (ground singlet state).
      Wszystkie elektrony sparowane, spin całkowity = 0.
      Punkt odniesienia (E = 0).</li>
  <li><b>S₁</b> — <b>pierwszy wzbudzony stan singletowy</b>.
      Jeden elektron przeniesiony na wyższy orbital, ale ze
      zachowaniem sparowania spinów (spin ogólny = 0).</li>
  <li><b>T₁</b> — <b>pierwszy wzbudzony stan trypletowy</b>.
      Jeden elektron na wyższym orbitalu, ale z
      <b>rozparowanym spinem</b> (spin całkowity = 1).</li>
</ul>

<h3>Dlaczego T₁ jest zawsze niżej niż S₁?</h3>
<p>
To wynika z <b>zasady Hunda dla cząsteczek</b>: dla tej samej
konfiguracji elektronowej stan trypletowy ma niższą energię niż
singletowy, ponieważ elektrony o tym samym spinie unikają się w
przestrzeni (wymiana), co obniża energię odpychania elektronowego.
Różnica S₁ − T₁ nazywa się <b>rozszczepieniem singlet-tryplet</b>
(ΔE<sub>ST</sub>) i jest kluczowa w projektowaniu emiterów TADF
(<i>Thermally Activated Delayed Fluorescence</i>).
</p>

<h3>Elementy diagramu</h3>
<ul>
  <li><b>S₀ (granatowa linia)</b> — stan podstawowy, energia = 0.</li>
  <li><b>T₁ (zielona linia)</b> — stan trypletowy.</li>
  <li><b>S₁ (bordowa linia)</b> — stan singletowy, zwykle najwyższy
      z trzech.</li>
  <li><b>Strzałka "Abs."</b> — absorpcja fotonu (S₀ → S₁).
      To proces promienisty, zachowujący spin.</li>
  <li><b>Krzywa przerywana "ISC"</b> — <b>Intersystem Crossing</b>
      (przejście międzysystemowe) ze stanu S₁ do T₁. Proces
      <b>bezpromienisty</b>, wymagający sprzężenia spinowo-orbitalnego.</li>
</ul>

<h3>Dlaczego ISC jest "zakrzywiona i przerywana"?</h3>
<p>
Linia przerywana podkreśla że ISC jest <b>zabronione spinowo</b>
(Δs ≠ 0). W cząsteczkach zawierających ciężkie atomy (Br, I, metale)
sprzężenie spinowo-orbitalne umożliwia ten "zakazany" proces.
Zakrzywiona trajektoria sugeruje że nie jest to natychmiastowe
przejście, lecz proces kinetyczny o charakterystycznej stałej szybkości
k<sub>ISC</sub>.
</p>

<h3>Interpretacja praktyczna</h3>
<ul>
  <li><b>Fosforescencja</b> zachodzi z T₁ do S₀ — wymaga wcześniejszego
      ISC z S₁.</li>
  <li><b>Fluorescencja</b> zachodzi z S₁ do S₀ — konkuruje z ISC.</li>
  <li><b>Tlen singletowy</b> (fotosensybilizacja) jest generowany przez
      cząsteczki o wysokim stopniu zapełnienia T₁ po absorpcji.</li>
</ul>

<h3>⚠️ Uwaga</h3>
<p>
Energie z TD-DFT zależą <b>silnie</b> od wyboru funkcjonału. Dla
przejść z transferem ładunku (CT) zalecane są funkcjonały
zakresowo-poprawione (CAM-B3LYP, ωB97X-D). Dla typowych
stanów π→π* wystarcza B3LYP lub PBE0.
</p>
"""


# ---------------------------------------------------------------------------
# Sekcja 3: Diagram Franck-Condon
# ---------------------------------------------------------------------------

FRANCK_CONDON_HTML = """
<h2>🟠 Diagram Franck-Condon</h2>

<h3>Co przedstawia diagram?</h3>
<p>
Diagram Franck-Condon pokazuje <b>powierzchnie energii potencjalnej</b>
(PES) dwóch lub trzech stanów elektronowych (S₀, T₁, S₁) <b>wzdłuż
uogólnionej współrzędnej reakcji r</b>. Ilustruje energetykę przejść
elektronowych w kontekście <b>drgań molekularnych</b>.
</p>
<p>
To <b>najbogatszy informacyjnie diagram</b> w spektroskopii molekularnej
i fotochemii — łączy energetykę elektronową z dynamiką jądrową.
</p>

<h3>Kluczowe koncepcje</h3>

<h4>1. Zasada Franck-Condon</h4>
<p>
Podczas absorpcji lub emisji fotonu <b>jądra atomowe są znacznie
wolniejsze od elektronów</b> (zasada Borna-Oppenheimera + duża różnica
mas). Oznacza to że przejście elektronowe zachodzi <b>przy niezmienionej
geometrii jądrowej</b> (przejście <i>pionowe</i>, ang. <i>vertical</i>).
</p>
<p>
Na diagramie widać to jako <b>pionową, pełną strzałkę</b> od minimum S₀
w górę — elektron wchodzi do stanu S₁ w geometrii S₀, która dla S₁
jest geometrią wysoko-energetyczną (zwykle na ścianie studni, nie w
minimum).
</p>

<h4>2. Różnica energii wertykalnej i adiabatycznej</h4>
<ul>
  <li><b>E<sub>vertical</sub> (wertykalna)</b> — energia przejścia
      przy niezmienionej geometrii. To energia absorbowanego fotonu
      (maksimum pasma absorpcji).</li>
  <li><b>E<sub>adiabatic</sub> (adiabatyczna)</b> — różnica energii
      między <b>minimami</b> obu stanów. Każdy stan w swojej
      zrelaksowanej geometrii.</li>
  <li>Różnica E<sub>vertical</sub> − E<sub>adiabatic</sub> to
      <b>energia reorganizacji</b> λ — miara sprzężenia
      elektron-fonon. Duża λ = silne przesunięcie Stokesa.</li>
</ul>

<h4>3. Relaksacja Kashy</h4>
<p>
Po absorpcji cząsteczka znajduje się w wysoko-wibracyjnym stanie S₁.
<b>Szybko</b> (pikosekundy) relaksuje wibracyjnie do minimum S₁
(zielona strzałka kropkowana w dół). Dalsza fluorescencja zachodzi
z tego minimum — dlatego widmo emisji nie zależy od długości fali
wzbudzenia.
</p>

<h3>Elementy diagramu</h3>
<ul>
  <li><b>Trzy krzywe potencjalne</b> (przypominające potencjał Morse'a) —
      S₀ (dolna), T₁ (środkowa), S₁ (górna). Minima są <b>przesunięte
      horyzontalnie</b>, bo stany wzbudzone mają inne geometrie
      równowagowe niż stan podstawowy.</li>
  <li><b>Poziomy wibracyjne</b> (poziome cienkie linie w studniach) —
      schematyczne drgania molekularne, ν=0, 1, 2...</li>
  <li><b>Funkcje falowe</b> (małe garby nad ν=0) — gęstość
      prawdopodobieństwa znalezienia jąder w stanie ν=0.</li>
  <li><b>Strzałka pionowa pełna</b> — przejście wertykalne (FC).</li>
  <li><b>Strzałka przerywana pochyła</b> — przejście adiabatyczne
      (między minimami).</li>
  <li><b>Krzywa "ISC"</b> — przejście międzysystemowe S₁ → T₁.</li>
  <li><b>Etykiety energii</b> — wartości E<sub>vertical</sub> i
      E<sub>adiabatic</sub> w kcal/mol lub eV.</li>
</ul>

<h3>Interpretacja praktyczna</h3>
<ul>
  <li><b>Małe przesunięcie Stokesa</b> (E<sub>vert</sub> ≈ E<sub>ad</sub>):
      sztywna cząsteczka, wąskie pasma, wysoka wydajność fluorescencji.</li>
  <li><b>Duże przesunięcie Stokesa</b> (E<sub>vert</sub> − E<sub>ad</sub>
      &gt; 0.5 eV): elastyczna cząsteczka, szerokie pasma,
      konkurencja bezpromienista.</li>
  <li>Jeśli <b>krzywe S₁ i S₀ się przecinają</b>: istnieje
      <b>stożek przecięcia</b> (conical intersection) — bardzo szybka
      relaksacja bezpromienista. Cząsteczka zachowuje się jak
      fotoprzełącznik.</li>
</ul>

<h3>📝 Ważne: ten diagram jest SCHEMATEM</h3>
<p>
W aplikacji DFT Visualizer krzywe potencjalne mają <b>kształt
schematyczny</b> (nie są wyliczane z rzeczywistych częstotliwości
drgań). Pokazujemy <b>poprawną topologię energetyczną</b> z realnymi
wartościami liczbowymi, ale szerokość studni i dokładny kształt
Morse'a są standardowe dla ułatwienia porównań między związkami.
Aby uzyskać dokładne krzywe trzeba wykonać skanowanie PES i obliczyć
modes normalne.
</p>
"""


# ---------------------------------------------------------------------------
# Dodatkowa sekcja: o metodach DFT/TD-DFT
# ---------------------------------------------------------------------------

METHODS_HTML = """
<h2>🔬 O metodach DFT i TD-DFT</h2>

<h3>Skąd biorą się liczby do tej aplikacji?</h3>
<p>
Dane wprowadzane do DFT Visualizer pochodzą zwykle z obliczeń
kwantowo-chemicznych w programach takich jak
<b>Gaussian, ORCA, Q-Chem, Turbomole, NWChem</b>. Typowy workflow:
</p>
<ol>
  <li><b>Optymalizacja geometrii</b> cząsteczki w stanie S₀
      (minimum energetyczne).</li>
  <li><b>Obliczenia częstotliwości drgań</b> — potwierdzenie
      że to rzeczywiście minimum (brak ujemnych wartości własnych
      Hessjanu).</li>
  <li><b>Pojedynczy punkt TD-DFT</b> na zoptymalizowanej geometrii S₀
      → daje energie S₁ i T₁ <b>wertykalne</b>.</li>
  <li><b>Osobna optymalizacja S₁ i T₁</b> (tryb TD-DFT opt) →
      daje energie <b>adiabatyczne</b>.</li>
  <li>Energie HOMO i LUMO odczytuje się bezpośrednio z
      obliczeń DFT dla stanu S₀.</li>
</ol>

<h3>Rekomendowane funkcjonały</h3>
<ul>
  <li><b>B3LYP</b> — klasyczny, dobry do stanów π→π*, słaby dla CT.</li>
  <li><b>PBE0</b> — podobnie do B3LYP, często lepszy dla związków
      organicznych.</li>
  <li><b>CAM-B3LYP</b> — zakresowo-poprawiony, zalecany dla stanów
      z transferem ładunku.</li>
  <li><b>ωB97X-D</b> — zakresowo-poprawiony + korekcja dyspersji.
      "Bezpieczny wybór" dla większości fotoaktywnych cząsteczek.</li>
</ul>

<h3>Bazy funkcyjne</h3>
<p>
Dla cząsteczek organicznych zwykle wystarcza
<b>6-31G(d,p)</b> lub <b>def2-SVP</b>. Dla dokładniejszych energii:
<b>6-311+G(d,p)</b> lub <b>def2-TZVP</b>. Dla stanów Rydbergowskich
konieczne są funkcje dyfuzyjne (+).
</p>

<h3>Format danych wejściowych</h3>
<p>
Aplikacja odczytuje plik Excel (.xlsx) z trzema arkuszami:
</p>
<ul>
  <li><b>HOMO_LUMO</b> — kolumny: <i>Compound, HOMO, LUMO</i> (w eV).</li>
  <li><b>States</b> — kolumny: <i>Compound, S0, T1, S1</i> (w eV).</li>
  <li><b>FranckCondon</b> — kolumny: <i>Compound, State, E_vertical,
      E_adiabatic, BDE_value, BDE_label</i> (w kcal/mol).
      Jedna cząsteczka może mieć wiele wierszy.</li>
</ul>
<p>
Przykładowy plik <code>sample_compounds.xlsx</code> znajduje się
w katalogu projektu.
</p>
"""


# ---------------------------------------------------------------------------
# Indeks i strona główna
# ---------------------------------------------------------------------------

OVERVIEW_HTML = """
<h1>📚 Teoria diagramów DFT</h1>

<p>
Ta sekcja wyjaśnia <b>znaczenie fizyczne</b> każdego z trzech typów
diagramów generowanych przez DFT Visualizer oraz koncepcje z
obliczeń kwantowo-chemicznych stojące za danymi wejściowymi.
</p>

<p>
Wybierz temat z listy po lewej stronie:
</p>

<ul>
  <li>🔴 <b>HOMO/LUMO</b> — energie orbitali granicznych,
      reaktywność chemiczna.</li>
  <li>🟢 <b>Stany S₀/S₁/T₁</b> — stany elektronowe, absorpcja i
      przejścia międzysystemowe.</li>
  <li>🟠 <b>Franck-Condon</b> — powierzchnie energii potencjalnej,
      przesunięcie Stokesa.</li>
  <li>🔬 <b>Metody obliczeniowe</b> — DFT, TD-DFT, rekomendacje dla
      funkcjonałów i baz.</li>
</ul>

<hr>

<p style="color: gray; font-size: small;">
<i>Ta aplikacja ma charakter wizualizacyjny. Dokładność wyników zależy
od jakości obliczeń źródłowych. Dla referencji naukowych podawaj zawsze
użyty funkcjonał i bazę obliczeń.</i>
</p>
"""


# ---------------------------------------------------------------------------
# Publiczny API
# ---------------------------------------------------------------------------

THEORY_SECTIONS: dict[str, tuple[str, str]] = {
    "overview":      ("📚 Przegląd",                  OVERVIEW_HTML),
    "homo_lumo":     ("🔴 HOMO / LUMO",              HOMO_LUMO_HTML),
    "states":        ("🟢 Stany S₀ / S₁ / T₁",       STATES_HTML),
    "franck_condon": ("🟠 Diagram Franck-Condon",    FRANCK_CONDON_HTML),
    "methods":       ("🔬 Metody DFT / TD-DFT",      METHODS_HTML),
}
"""Mapping section_key -> (display_name, html_content).

Use this to populate the theory window's navigation list and content pane.
"""
