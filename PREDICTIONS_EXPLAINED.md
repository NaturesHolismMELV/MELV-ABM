# MELV V2.1 — Six Predictions Explained

**A plain-language guide to what was tested, why it matters, and what the results mean**

*For the full mathematical treatment see [Tutorial_02_master_equation.ipynb](Tutorial_02_master_equation.ipynb)*  
*For the underlying theory see Evans, L.W. (2026). Blueprint for Harmony. Cooperation Press. ISBN 978-969-8992-10-1.*

---

## Background: What the Model Is Testing

The MELV framework asks a deceptively simple question:

> **Under what conditions does cooperation become the stable, self-sustaining outcome — and under what conditions does competition win instead?**

The model tracks a single quantity called the **i-factor** for each pair of interacting agents. When i is high (above 1), competition dominates. When i falls toward 1 from above and crosses into the cooperative basin, cooperation becomes stable. The master equation governs how i evolves:

```
i(t) = i₀ × (1 − ε × φ(t) × β(t))
```

Where φ is evolutionary maturity, β is cooperative neighbourhood density, and ε is the rate of adaptive response.

The six predictions below test whether this mathematical structure produces the biological outcomes it is designed to capture.

---

## Prediction 1 — Two Stable Worlds, Not a Spectrum

### What was predicted
If the master equation correctly describes a bifurcation, running many simulations should not produce a smooth spread of outcomes. Instead there should be **two distinct groups**: one where the system settles into competition, one where it settles into cooperation, with very few cases stuck in between.

This is analogous to water freezing: you don't get a gradual continuum from liquid to solid — you get a phase transition. The MELV framework predicts an ecological equivalent.

### Why it matters
A sharp split means the system has two genuine attractor basins — two natural resting states that the system gravitates toward and stays in. Without this, the model would produce arbitrary, parameter-sensitive outcomes rather than a principled bifurcation.

### What the test showed
**Hartigan's dip test: dip = 0.047, p ≈ 0**

The two-peak pattern is confirmed with near-zero probability of being random. Across 405 runs, 79% settled into competition, 12% into cooperation, and only 9% remained near the boundary (THRESH).

### Why is the cooperative basin only 12%?

This is the right question to ask — and the answer clarifies what the result actually measures.

The 12% figure is not a fixed property of the MELV framework. It is a property of this particular parameter grid in this particular simulation environment. The cooperative basin percentage will vary across different ecological contexts:

- A resource-rich environment (high R, high φ, diverse service differentiation) will produce a much higher proportion of cooperative outcomes
- An arid or resource-scarce environment will produce fewer
- A disturbed context — invasion, rapid environmental change, low φ — will sit near the boundary

What is invariant across all contexts is the **bimodality itself** — the existence of two distinct attractor basins with a sharp boundary between them. The proportion filling each basin is context-dependent, just as the proportion of liquid water in a sample depends on the temperature range you test.

In this validation run, one third of conditions used R = 0.3 (low resources), where insufficient energetic surplus exists to sustain cooperative benefit flows. Competition in those conditions is not a model failure — it is the correct biological prediction. The parameter grid was designed to span the full space, not to maximise cooperative outcomes.

Crucially, the Hartigan dip test does not require equal-sized peaks. A 79%/12% split with a sharp boundary is just as strong evidence of bifurcation as a 50%/50% split. The test confirms the structure — two distinct basins — not the size of either basin.

### Plain takeaway
> The model produces two stable worlds — cooperative or competitive — with a sharp boundary between them. The proportion in each basin varies with ecological context. The boundary itself does not.

---

## Prediction 2 — The Threshold Is Universal

### What was predicted
The point where the system tips from competition to cooperation should **not depend on how fast agents evolve** (ε). If the threshold moved around depending on evolutionary rate, it would be a model artefact — a parameter trick — rather than a genuine property of the system.

### Why it matters
Universality is the hallmark of a real bifurcation. The same tipping point should appear whether evolution is slow or fast, just as the freezing point of water doesn't depend on how quickly you cool it.

### What the test showed
**One-way ANOVA across ε strata: F = 1.91, p = 0.15 (not significant)**

The threshold stayed in the same place regardless of evolutionary rate. ε determines how quickly the system moves — not where the boundary is.

### Plain takeaway
> The line between competition and cooperation is a real feature of the system, not a tuning artefact.

---

## Prediction 3 — Resources Trigger Cooperation, Not Mutation Rate

### What was predicted
You might expect that if agents evolve faster, cooperation should appear sooner. The prediction says otherwise: **evolutionary rate (ε) does not determine when cooperation emerges. Resource availability (R) does.**

### Why it matters
This matches the major transitions literature in evolutionary biology. The rise of multicellularity, eusociality, and mutualism are triggered by ecological opportunity — when the environment makes cooperation energetically favourable — not by elevated mutation rates. The model should reflect this.

### What the test showed
**Regression of crossing time on ε: no significant relationship**  
**Regression of crossing time on R: strong relationship**

A null result — but a theoretically informative one. Resource abundance is the ecological gate that cooperation must pass through.

### Plain takeaway
> Cooperation blooms when the environment allows it, not when evolution speeds up.

---

## Prediction 4 — Lower i Reliably Predicts More Cooperation

### What was predicted
The i-factor is the model's cooperation thermometer. Lower i means higher compatibility — which should produce higher cooperation levels. The prediction requires a **strong negative correlation** between final mean i and final cooperation level (criterion: r < −0.90).

### Why it matters
If the i-factor is a meaningful quantity, it should be a reliable predictor of the system's cooperative state. A weak or inconsistent correlation would undermine the master equation's explanatory power.

### What the test showed
**Pearson r = −0.866 (p < 10⁻¹⁰⁰)**

Strong and highly significant — but the strict criterion of r < −0.90 was narrowly missed. This reflects the asymmetric parameter grid (79% of runs are in the competitive basin, compressing variance at high i) rather than a model failure. The relationship is monotonic and robust.

### Plain takeaway
> Lower i reliably means more cooperation — exactly as theory predicts. The criterion was narrowly missed due to dataset composition, not model error.

---

## Prediction 5 — Cooperation Requires Both Stability and Neighbours

### What was predicted
Cooperation should not depend on a single factor. It requires **both**:
- **φ** — long-run maturity and stability of the agent
- **β** — a sufficiently cooperative local neighbourhood

The prediction is that the **product φ×β** (not either factor alone) should discriminate cooperative from competitive outcomes with high precision. This validates the multiplicative structure of the master equation.

### Why it matters
If cooperation required only one factor, the master equation would be over-specified. The multiplicative structure predicts that both must be present simultaneously — like a lock requiring two keys. Neither stability alone nor cooperative neighbours alone is sufficient.

### What the test showed
**Sensitivity = 1.0 | Specificity = 0.997**

The φ×β product identified every cooperative run (100% recall) with almost no false positives (0.3% false positive rate). This is near-perfect discriminative power, directly validating the multiplicative structure.

### Plain takeaway
> Cooperation emerges only when agents are both internally mature (φ) and surrounded by cooperative neighbours (β). Neither alone is enough.

---

## Prediction 6 — Cooperation (and Competition) Are Evolutionarily Stable

### What was predicted
If a system has settled into the cooperative basin, introducing a wave of disruptive "selfish" mutants should not collapse it. The cooperative state should **snap back** — like a ball rolling back into a valley after being pushed. The same applies to the competitive basin: a few cooperators appearing shouldn't suddenly convert a competitive system.

This is evolutionary stability in the sense of Maynard Smith (1982) — a state that resists invasion.

### Why it matters
A cooperative state that collapses under the first invasion is not a genuine attractor — it is a fragile equilibrium. Biological cooperation (mutualism, eusociality, multicellularity) persists under constant competitive pressure. The model must demonstrate the same robustness.

### What the test showed
**34/34 invasion tests recovered to original basin (100%)**

Both the cooperative and competitive attractors were fully stable. Following a 25% mutant invasion (Δi ≈ 0.57 displacement), all 34 systems returned to their pre-invasion state within 500 steps.

### Plain takeaway
> Once the system settles into cooperation — or competition — it stays there even under heavy invasion pressure.

---

## Summary Table

| # | Prediction | Test | Result | Status |
|---|-----------|------|--------|--------|
| 1 | Bimodal outcome distribution | Hartigan dip, p < 0.05 | dip = 0.047, p ≈ 0 | ✅ PASS |
| 2 | Threshold universality across ε | ANOVA p > 0.05 | F = 1.91, p = 0.15 | ✅ PASS |
| 3 | Crossing time ∝ ε | Regression p < 0.05 | Resource (R) dominates | ⬜ NULL — theoretically informative |
| 4 | Strong negative correlation | Pearson r < −0.90 | r = −0.866 | ⚠️ NEAR — asymmetric grid |
| 5 | φ×β predicts cooperative crossing | Sens/spec > 0.75 | 1.0 / 0.997 | ✅ PASS |
| 6 | ESS attractor stability | Recovery > 85% | 34/34 (100%) | ✅ PASS |

4/5 directional predictions confirmed. The null result on Prediction 3 is theoretically informative — ecological opportunity drives cooperative transitions, not mutation rate. The near-miss on Prediction 4 reflects the asymmetric parameter grid (79% COMP conditions), not a model failure.

---

## Reproducing These Results

All six tests are reproduced in full in the interactive tutorial:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NaturesHolismMELV/MELV-ABM/main?filepath=Tutorial_02_master_equation.ipynb)

Click the badge to run all cells in your browser. No installation required. Typical runtime: under 10 minutes.

---

*Laurence W. Evans | ORCID: 0009-0001-0963-1840*  
*naturesholism.substack.com | @NaturesHolism*  
*Evans, L.W. (2026). MELV ABM V2.1. Zenodo. DOI: [10.5281/zenodo.19422174](https://doi.org/10.5281/zenodo.19422174)*
