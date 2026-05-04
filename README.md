# MELV-ABM: Agent-Based Validation of the MELV Cooperation Threshold

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NaturesHolismMELV/MELV-ABM/main?filepath=Tutorial_02_master_equation.ipynb)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19422174.svg)](https://doi.org/10.5281/zenodo.19422174)

**Reproducible agent-based validation of the Modified Energetic Lotka-Volterra (MELV) framework**

This repository contains the complete ABM V2.1 implementation, all validation data, and an interactive tutorial notebook allowing peer reviewers and researchers to reproduce every reported result directly in the browser — no installation required.

---

## Quick Start: Reproduce the Results

**Click the Binder badge above** to launch an interactive environment where you can:
- Inspect all 405 simulation runs
- Reproduce the six prediction tests (including Hartigan dip, ANOVA, φ×β sensitivity)
- Run the ESS invasion analysis (34/34 recovery)
- Visualise all seven publication figures from the underlying data

Or run locally — see [Installation](#installation) below.

---

## 1. Overview

This repository provides computational validation for the cooperation threshold predicted by the Modified Energetic Lotka-Volterra (MELV) framework (Evans, 2026). Version 2.1 extends V2.0 with three biologically motivated architectural improvements and two new validation modules — an ESS mutant invasion test and a trajectory convergence analysis — that together upgrade the attractor basin evidence from *"consistent with"* to *"demonstrates"*.

The model confirms that the critical bifurcation near i → 1 emerges spontaneously from evolutionary selection dynamics, is stable against 25% mutant invasion (34/34 tests, 100% recovery), and produces populations that converge to and remain in distinct attractor basins with near-zero late-time drift.

**Implementation:** Python / Mesa 3.5 | 81 parameter conditions × 5 replicates = **405 runs** | 2000 steps per run

---

## 2. The MELV Master Equation

```
i₁₂(t) = i₁₂⁰ × (1 − ε × φ(t) × β(t))
```

| Symbol | Definition |
|--------|------------|
| i₁₂(t) | Compatibility factor between agents at time t |
| i₁₂⁰   | Initial compatibility |
| ε       | Evolutionary rate (adaptation acceleration) |
| φ(t)    | Perpetuity — long-run relational stability [0, 1] |
| β(t)    | Cooperative neighbourhood density (Omega proxy) |
| φ × β   | Joint driver of cooperation — the phi-beta product |

The equation is dimensionless — i₁₂(t) functions analogously to a refractive index, describing the fraction of potential cooperative benefit realised at time t. Full cooperative convergence (Cooperation Index CI → 1.0) occurs as i approaches its theoretical maximum near unity.

### Bifurcation threshold

Empirically determined at **i = 0.9995 ± 0.029** (R² = 0.9248, p < 10⁻³⁰⁰). Runs with final mean i < 0.9 are classified COOP; i > 1.1 are COMP; between are THRESH.

---

## 3. V2.1 Architecture

Three biologically motivated improvements over V2.0:

### Sigmoid Allee effect (cooperator efficiency)
Cooperator advantage is a logistic function of local β — below the quorum threshold (τ = 0.5), cooperation is suppressed regardless of individual i-factor. This is mathematically equivalent to bacterial quorum sensing (Nadell et al., 2016) and the Allee effect (Courchamp et al., 1999).

```python
efficiency_coop = 1.0 + (1 − i_factor) × sigmoid(β, k=10, τ=0.5) × φ
```

### Frequency-dependent suppression (competitor efficiency)
Competitive advantage scales as (1 − β)² — accelerating as cooperative density collapses, stabilising the competitive attractor (Gore et al., 2009; Nowak & May, 1992).

```python
efficiency_comp = 1.1 + (i_factor − 1.0) × (1 − β)²
```

### 20×20 spatial grid
Reduces stochastic drift that masked attractor structure in the 10×10 grid, enabling spatial cooperative cluster dynamics consistent with Nadell et al. (2016) and Tarnita et al. (2011).

---

## 4. Results Summary

| # | Prediction | Test | Criterion | Result |
|---|-----------|------|-----------|--------|
| 1 | Bimodal i distribution | Hartigan dip | p < 0.05 | **PASS** — dip = 0.047, p ≈ 0 |
| 2 | Threshold universality | ANOVA across ε | p > 0.05 | **PASS** — F = 1.91, p = 0.15 |
| 3 | Crossing time ∝ ε | Linear regression | p < 0.05 | **NULL** — resource availability dominates |
| 4 | Strong negative correlation | Pearson r | r < −0.90 | r = −0.866 (strong; criterion slightly missed) |
| 5 | φ×β predicts crossing | Sensitivity/specificity | both > 0.75 | **PASS** — sens = 1.0, spec = 0.997 |
| 6 | ESS attractor stability | Invasion recovery | > 85% | **PASS** — 34/34, 100% |

### Outcome distribution (405 runs)

| Outcome | n | % |
|---------|---|---|
| COOP    | 48 | 12% |
| COMP    | 319 | 79% |
| THRESH  | 38 | 9% |

THRESH reduction from 68% (V2.0) to 9% (V2.1) reflects the Allee effect creating genuine basin separation. Competitive-basin dominance (79%) accurately reflects that the parameter grid spans many resource-limited, low-interaction conditions where competitive dynamics are the biologically expected outcome.

---

## 5. Repository Structure

```
MELV-ABM/
├── melv_abm_v2_1.py                  # Core ABM: MELVAgent + MELVModel
├── batch_run_v2_1_2000.py            # Batch sweep: 81 conditions × 5 replicates
├── perturbation_test.py              # ESS mutant invasion test
├── figure_07_trajectory_convergence.py
├── Tutorial_02_master_equation.ipynb # ← Interactive tutorial for peer reviewers
├── data/
│   ├── validation_summary_v2_1_2000.csv   # Final-step summary (405 runs)
│   ├── validation_data_v2_1_2000.csv      # Full trajectories (every 10 steps)
│   └── perturbation_results.csv           # Invasion recovery results (34 tests)
├── figures/
│   ├── figure_01_bimodal.png
│   ├── figure_02_correlation.png
│   ├── figure_03_universality.png
│   ├── figure_04_crossing_time.png
│   ├── figure_05_perturbation.png
│   ├── figure_06_invasion_trajectories.png
│   └── figure_07_trajectory_convergence.png
├── preliminary/
│   └── raw_data/                     # Earlier (Nov 2025) eigenvalue-based runs
├── requirements.txt
├── environment.yml
└── README.md
```

---

## 6. Installation

Python 3.12+ required.

```bash
git clone https://github.com/NaturesHolismMELV/MELV-ABM.git
cd MELV-ABM
pip install -r requirements.txt
```

### Run the full batch sweep

```bash
python batch_run_v2_1_2000.py
```

405 runs × 2000 steps. Completes in ~260 seconds. Writes two CSV files.

### Run the ESS invasion test

```bash
python perturbation_test.py
```

34 invasion tests. Prints recovery rate. Saves Figures 5–6.

### Run a single model (quick test)

```bash
python melv_abm_v2_1.py
```

5 test configurations. Passes if ≥1 COOP and ≥1 COMP are present.

---

## 7. Version History

| Version | Date | Platform | Conditions | Key features |
|---------|------|----------|-----------|--------------|
| V1 | Oct 2025 | JavaScript (browser) | 27 | Single replicates, fixed ε |
| V2.0 | Apr 2026 | Python / Mesa 3.5 | 81 × 5 | Heritable i-factor, fitness selection, ε axis |
| V2.1 | Apr 2026 | Python / Mesa 3.5 | 81 × 5 | Sigmoid Allee effect, 20×20 grid, invasion test, 2000 steps |

Earlier preliminary data (eigenvalue-based mutualism network model, Nov 2025) is archived in `preliminary/raw_data/` for development transparency.

---

## 8. Citation

```
Evans, L.W. (2026). Agent-Based Validation of the MELV Cooperation Threshold:
Version 2.1. Zenodo. https://doi.org/10.5281/zenodo.19422174

Evans, L.W. (2026). Blueprint for Harmony: A Mathematical Framework for
Cooperative Systems. Cooperation Press. ISBN 978-969-8992-10-1.

MELV Framework Preprint:
Evans, L.W. (2026). https://doi.org/10.5281/zenodo.19029077
```

---

## 9. License

**CC BY 4.0** — https://creativecommons.org/licenses/by/4.0/

---

**Author:** Laurence W. Evans (Zaid)
**ORCID:** [0009-0001-0963-1840](https://orcid.org/0009-0001-0963-1840)
**Substack:** [naturesholism.substack.com](https://naturesholism.substack.com)
**X:** [@NaturesHolism](https://x.com/NaturesHolism)

*Key references: Allee (1931); Axelrod & Hamilton (1981); Courchamp, Clutton-Brock & Grenfell (1999); Gore, Youk & van Oudenaarden (2009); Nadell, Drescher & Foster (2016); Nowak & May (1992); Tarnita et al. (2011).*
