"""Theoretical content for the 'Theory' window (English, medium detail level).

Content aimed at master's / early-PhD students working with DFT/TD-DFT
calculations. Goal: after 5 minutes of reading, the user understands
what each of the three diagrams shows and why any given element looks
the way it does.

Uses HTML with subset supported by Qt's QTextBrowser (basic HTML + CSS).
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Section 1: HOMO/LUMO
# ---------------------------------------------------------------------------

HOMO_LUMO_HTML = """
<h2>🔴 HOMO/LUMO Diagram</h2>

<h3>What does the diagram show?</h3>
<p>
The <b>HOMO/LUMO</b> diagram displays the energies of the two most
important frontier molecular orbitals:
</p>
<ul>
  <li><b>HOMO</b> (<i>Highest Occupied Molecular Orbital</i>) — the
      highest-energy orbital that still holds electrons. It represents
      the "top" of the occupied electronic structure of the molecule.</li>
  <li><b>LUMO</b> (<i>Lowest Unoccupied Molecular Orbital</i>) — the
      lowest-energy orbital with no electrons. It is the first "free"
      orbital available to accept an excited electron.</li>
</ul>

<h3>Why are these two orbitals important?</h3>
<p>
HOMO and LUMO define the <b>chemical reactivity</b> of the molecule:
</p>
<ul>
  <li>The HOMO energy indicates the ability to <b>donate electrons</b>
      (ionization potential, ~IP). Higher HOMO = easier oxidation.</li>
  <li>The LUMO energy describes the ability to <b>accept electrons</b>
      (electron affinity, ~EA). Lower LUMO = easier reduction.</li>
  <li>The <b>LUMO − HOMO</b> energy difference, known as the
      <b>HOMO/LUMO gap</b>, is a first approximation of the electronic
      and optical excitation energy.</li>
</ul>

<h3>Elements of the diagram</h3>
<ul>
  <li><b>Red horizontal lines</b> — HOMO levels for each molecule
      (color is configurable).</li>
  <li><b>Blue horizontal lines</b> — LUMO levels.</li>
  <li><b>Vertical arrow with value</b> — magnitude of the HOMO/LUMO
      gap, usually in eV.</li>
  <li><b>Numeric values beside each line</b> — orbital energies in eV
      (negative values — energies are referenced to the vacuum level).</li>
</ul>

<h3>Practical interpretation</h3>
<p>
Molecules with a <b>small HOMO/LUMO gap</b> tend to be:
</p>
<ul>
  <li>More photochemically reactive.</li>
  <li>Absorbers of longer-wavelength light (bathochromic shift).</li>
  <li>Commonly used as chromophores and organic dyes.</li>
</ul>
<p>
Molecules with a <b>large gap</b> tend to be stable, colorless, and
less reactive.
</p>

<h3>⚠️ Methodological note</h3>
<p>
HOMO and LUMO energies computed with <b>DFT</b> (e.g., B3LYP) are
<b>only approximations</b> of the true Kohn-Sham orbital energies.
Accurate values of IP and EA require separate calculations (Δ-SCF or
Green's-function methods). DFT typically <b>underestimates</b> the true
optical gap by 30–50%.
</p>
"""


# ---------------------------------------------------------------------------
# Section 2: Electronic states S0/S1/T1
# ---------------------------------------------------------------------------

STATES_HTML = """
<h2>🟢 Electronic State Diagram (S₀/S₁/T₁)</h2>

<h3>What does the diagram show?</h3>
<p>
This diagram shows the <b>energies of electronic states</b> of the
molecule, usually obtained from <b>TD-DFT</b> (<i>Time-Dependent Density
Functional Theory</i>):
</p>
<ul>
  <li><b>S₀</b> — <b>singlet ground state</b>. All electrons paired,
      total spin = 0. The reference point (E = 0).</li>
  <li><b>S₁</b> — <b>first excited singlet state</b>. One electron
      promoted to a higher orbital, but spins remain paired (total
      spin = 0).</li>
  <li><b>T₁</b> — <b>first excited triplet state</b>. One electron at a
      higher orbital, but with <b>parallel spins</b> (total spin = 1).</li>
</ul>

<h3>Why is T₁ always below S₁?</h3>
<p>
This follows from <b>Hund's rule for molecules</b>: for the same
electronic configuration, the triplet state has lower energy than the
singlet because electrons of parallel spin avoid each other in space
(exchange), reducing the electron-electron repulsion. The S₁ − T₁
difference is called the <b>singlet-triplet splitting</b>
(ΔE<sub>ST</sub>) and is crucial in designing TADF (<i>Thermally
Activated Delayed Fluorescence</i>) emitters.
</p>

<h3>Elements of the diagram</h3>
<ul>
  <li><b>S₀ (navy blue line)</b> — ground state, energy = 0.</li>
  <li><b>T₁ (green line)</b> — triplet state.</li>
  <li><b>S₁ (dark red line)</b> — singlet state, typically the
      highest of the three.</li>
  <li><b>"Abs." arrow</b> — photon absorption (S₀ → S₁). A radiative,
      spin-conserving process.</li>
  <li><b>"ISC" dashed curve</b> — <b>Intersystem Crossing</b> from S₁
      to T₁. A <b>non-radiative</b> process requiring spin-orbit
      coupling.</li>
</ul>

<h3>Why is ISC "curved and dashed"?</h3>
<p>
The dashed style emphasizes that ISC is <b>spin-forbidden</b>
(Δs ≠ 0). Molecules containing heavy atoms (Br, I, metals) exhibit
enhanced spin-orbit coupling that enables this "forbidden" process.
The curved trajectory conveys that ISC is not instantaneous but a
kinetic process with a characteristic rate constant k<sub>ISC</sub>.
</p>

<h3>Practical interpretation</h3>
<ul>
  <li><b>Phosphorescence</b> occurs from T₁ to S₀ — it requires a
      preceding ISC from S₁.</li>
  <li><b>Fluorescence</b> occurs from S₁ to S₀ — it competes with ISC.</li>
  <li><b>Singlet oxygen</b> (photosensitization) is generated by
      molecules with high T₁ population after absorption.</li>
</ul>

<h3>⚠️ Note</h3>
<p>
TD-DFT state energies depend <b>strongly</b> on the choice of
functional. For charge-transfer (CT) states, range-separated
functionals (CAM-B3LYP, ωB97X-D) are recommended. For typical π→π*
states, B3LYP or PBE0 is sufficient.
</p>
"""


# ---------------------------------------------------------------------------
# Section 3: Franck-Condon diagram
# ---------------------------------------------------------------------------

FRANCK_CONDON_HTML = """
<h2>🟠 Franck-Condon Diagram</h2>

<h3>What does the diagram show?</h3>
<p>
The Franck-Condon diagram displays <b>potential energy surfaces</b>
(PES) of two or three electronic states (S₀, T₁, S₁) <b>along a
generalized reaction coordinate r</b>. It visualizes the energetics
of electronic transitions in the context of <b>molecular vibrations</b>.
</p>
<p>
This is the <b>most information-rich diagram</b> in molecular
spectroscopy and photochemistry — it unifies electronic energetics
with nuclear dynamics.
</p>

<h3>Key concepts</h3>

<h4>1. Franck-Condon principle</h4>
<p>
During photon absorption or emission, <b>atomic nuclei are much slower
than electrons</b> (Born-Oppenheimer approximation + large mass
difference). As a result, an electronic transition occurs
<b>at unchanged nuclear geometry</b> (a <i>vertical</i> transition).
</p>
<p>
On the diagram this manifests as a <b>vertical solid arrow</b> from
the S₀ minimum upward — the electron enters S₁ at the S₀ geometry,
which for S₁ is a high-energy geometry (typically on the wall of the
well, not at its minimum).
</p>

<h4>2. Vertical vs. adiabatic energy</h4>
<ul>
  <li><b>E<sub>vertical</sub></b> — excitation energy at unchanged
      geometry. It is the absorbed photon energy (absorption band
      maximum).</li>
  <li><b>E<sub>adiabatic</sub></b> — energy difference between the
      <b>minima</b> of both states. Each state at its own relaxed
      geometry.</li>
  <li>The difference E<sub>vertical</sub> − E<sub>adiabatic</sub> is
      the <b>reorganization energy</b> λ — a measure of
      electron-phonon coupling. Large λ = large Stokes shift.</li>
</ul>

<h4>3. Kasha relaxation</h4>
<p>
Immediately after absorption the molecule sits in a vibrationally hot
S₁ state. It then <b>rapidly</b> (picoseconds) relaxes vibrationally
to the S₁ minimum (green downward dotted arrow). Subsequent
fluorescence occurs from this minimum — which is why the emission
spectrum is independent of the excitation wavelength.
</p>

<h3>Elements of the diagram</h3>
<ul>
  <li><b>Three potential curves</b> (resembling Morse potentials) —
      S₀ (bottom), T₁ (middle), S₁ (top). Minima are <b>horizontally
      offset</b>, because the excited states have different equilibrium
      geometries than the ground state.</li>
  <li><b>Vibrational levels</b> (thin horizontal lines inside each well)
      — schematic molecular vibrations, ν=0, 1, 2...</li>
  <li><b>Wavefunctions</b> (small bumps above ν=0) — probability
      density of finding the nuclei in the ν=0 state.</li>
  <li><b>Vertical solid arrow</b> — vertical (FC) transition.</li>
  <li><b>Inclined dashed arrow</b> — adiabatic transition
      (between minima).</li>
  <li><b>"ISC" curve</b> — S₁ → T₁ intersystem crossing.</li>
  <li><b>Energy labels</b> — values of E<sub>vertical</sub> and
      E<sub>adiabatic</sub> in kcal/mol or eV.</li>
</ul>

<h3>Practical interpretation</h3>
<ul>
  <li><b>Small Stokes shift</b> (E<sub>vert</sub> ≈ E<sub>ad</sub>):
      rigid molecule, narrow bands, high fluorescence quantum yield.</li>
  <li><b>Large Stokes shift</b> (E<sub>vert</sub> − E<sub>ad</sub>
      &gt; 0.5 eV): flexible molecule, broad bands, competing
      non-radiative decay.</li>
  <li>If <b>S₁ and S₀ curves cross</b>: there is a <b>conical
      intersection</b> enabling very fast non-radiative relaxation.
      The molecule behaves like a photoswitch.</li>
</ul>

<h3>📝 Important: this diagram is a SCHEMATIC</h3>
<p>
In DFT Visualizer the potential curves have a <b>schematic shape</b>
(they are NOT computed from actual vibrational frequencies). We show
the <b>correct energetic topology</b> with real numerical values, but
the well widths and exact Morse shapes are standardized to make
comparisons between compounds easier. To obtain accurate PES curves,
one must perform a PES scan and compute the normal modes.
</p>
"""


# ---------------------------------------------------------------------------
# Section 4: DFT / TD-DFT methods
# ---------------------------------------------------------------------------

METHODS_HTML = """
<h2>🔬 About DFT and TD-DFT methods</h2>

<h3>Where do the numbers come from?</h3>
<p>
Data used in DFT Visualizer typically comes from quantum chemistry
calculations in packages like <b>Gaussian, ORCA, Q-Chem, Turbomole,
NWChem</b>. A typical workflow:
</p>
<ol>
  <li><b>Geometry optimization</b> of the molecule in S₀ (energy
      minimum).</li>
  <li><b>Vibrational frequency calculation</b> — confirms that the
      structure is indeed a minimum (no imaginary frequencies / no
      negative Hessian eigenvalues).</li>
  <li><b>TD-DFT single point</b> at the optimized S₀ geometry → yields
      <b>vertical</b> S₁ and T₁ energies.</li>
  <li><b>Separate S₁ and T₁ optimization</b> (TD-DFT opt mode) → yields
      <b>adiabatic</b> energies.</li>
  <li>HOMO and LUMO energies are read directly from the DFT calculation
      for the S₀ state.</li>
</ol>

<h3>Recommended functionals</h3>
<ul>
  <li><b>B3LYP</b> — classic, good for π→π* states, weaker for CT.</li>
  <li><b>PBE0</b> — similar to B3LYP, often better for organic molecules.</li>
  <li><b>CAM-B3LYP</b> — range-separated, recommended for
      charge-transfer states.</li>
  <li><b>ωB97X-D</b> — range-separated + dispersion correction.
      A "safe choice" for most photoactive molecules.</li>
</ul>

<h3>Basis sets</h3>
<p>
For organic molecules <b>6-31G(d,p)</b> or <b>def2-SVP</b> is typically
sufficient. For more accurate energies: <b>6-311+G(d,p)</b> or
<b>def2-TZVP</b>. For Rydberg states, diffuse functions (+) are
required.
</p>

<h3>Input data format</h3>
<p>
The application reads an Excel file (.xlsx) with three sheets:
</p>
<ul>
  <li><b>HOMO_LUMO</b> — columns: <i>Compound, HOMO, LUMO</i> (in eV).</li>
  <li><b>States</b> — columns: <i>Compound, S0, T1, S1</i> (in eV).</li>
  <li><b>FranckCondon</b> — columns: <i>Compound, State, E_vertical,
      E_adiabatic, BDE_value, BDE_label</i> (in kcal/mol). One molecule
      can have multiple rows.</li>
</ul>
<p>
A sample file <code>sample_compounds.xlsx</code> is provided in the
project directory.
</p>
"""


# ---------------------------------------------------------------------------
# Overview / landing page
# ---------------------------------------------------------------------------

OVERVIEW_HTML = """
<h1>📚 DFT Diagrams — Theoretical Background</h1>

<p>
This section explains the <b>physical meaning</b> of each of the three
diagram types generated by DFT Visualizer, and the quantum-chemistry
concepts behind the input data.
</p>

<p>
Select a topic from the list on the left:
</p>

<ul>
  <li>🔴 <b>HOMO/LUMO</b> — frontier orbital energies, chemical
      reactivity.</li>
  <li>🟢 <b>S₀/S₁/T₁ states</b> — electronic states, absorption, and
      intersystem crossing.</li>
  <li>🟠 <b>Franck-Condon</b> — potential energy surfaces, Stokes
      shift.</li>
  <li>🔬 <b>Computational methods</b> — DFT, TD-DFT, functional and
      basis-set recommendations.</li>
</ul>

<hr>

<p style="color: gray; font-size: small;">
<i>This application is a visualization tool. The accuracy of the
resulting figures depends on the quality of the underlying
calculations. When citing results, always report the functional and
basis set used.</i>
</p>
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

THEORY_SECTIONS: dict[str, tuple[str, str]] = {
    "overview":      ("📚 Overview",                  OVERVIEW_HTML),
    "homo_lumo":     ("🔴 HOMO / LUMO",              HOMO_LUMO_HTML),
    "states":        ("🟢 S₀ / S₁ / T₁ States",      STATES_HTML),
    "franck_condon": ("🟠 Franck-Condon Diagram",    FRANCK_CONDON_HTML),
    "methods":       ("🔬 DFT / TD-DFT Methods",     METHODS_HTML),
}
"""Mapping section_key -> (display_name, html_content).

Use this to populate the theory window's navigation list and content pane.
"""