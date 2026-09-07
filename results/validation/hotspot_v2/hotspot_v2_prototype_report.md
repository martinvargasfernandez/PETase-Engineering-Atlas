# Hotspot Prioritization V2 Prototype Report

**Date**: 2026-08-31

This report documents the design, formulas, and development diagnostic results for the Hotspot Prioritization V2 candidate models. 

---

## 1. Candidate Model Formulas

All candidate models were defined and pre-specified using transparent normalization before evaluating their performance on the 21 development hotspots.

* **FVI Normalization ($F_{\text{norm}}$)**: $(FVI - 1) / 6$ (normalized to range 0.0 to 1.0).
* **Shannon Entropy Normalization ($H_{\text{norm}}$)**: $H / \log_2(20)$ (normalized to range 0.0 to 1.0, where maximum theoretical entropy is 4.3219).
* **Pocket Proximity Score ($P_{\text{prox}}$)**: $\max(0, 1 - d_{\text{centroid}} / 20.0)$ (range 0.0 to 1.0, where $d_{\text{centroid}}$ is the Euclidean distance from the $C_\alpha$ atom to the active-site centroid of catalytic triad residues S160, D206, and H237).
* **Relative SASA ($S_{\text{sasa}}$)**: Residue SASA divided by max Gly-X-Gly tripeptide SASA.
* **Packing Density ($C_{\text{pack}}$)**: $\text{local\_contact\_count} / 20.0$ (ratio of $C_\alpha$ atoms within 8.0 Å, normalized to max 20).

### Candidate Models

#### Model E0: Current Evolutionary Baseline
> $S_{\text{E0}} = \text{evolutionary\_score}$ (range 0 to 7)

#### Model E1: Evolutionary Diversity Refined
> $S_{\text{E1}} = S_{\text{E0}} + 1.5 \times F_{\text{norm}} + 1.5 \times H_{\text{norm}}$ (range 0 to 10)

#### Model ES1: Evolution + Proximity
> $S_{\text{ES1}} = S_{\text{E1}} + 3.0 \times P_{\text{prox}}$ (range 0 to 13)

#### Model ES2: Evolution + Accessibility + Proximity
> $S_{\text{ES2}} = S_{\text{ES1}} + 1.5 \times S_{\text{sasa}} - 1.5 \times C_{\text{pack}}$ (range 0 to 14.5)

#### Model ES3: Structural-Prioritized Hybrid
> $S_{\text{ES3}} = (6.0 \times P_{\text{prox}} + 4.0 \times S_{\text{sasa}}) + 0.5 \times S_{\text{E1}}$ (range 0 to 15)

---

## 2. Model Performance Summary
The table below summarizes the diagnostic recovery metrics for all 5 pre-specified models evaluated against the 21 strict development hotspots (eligible universe N=243):

| Model | Top 5% (12) | Top 10% (24) | Top 20% (48) | Top 25% (60) | Median Rank | In Top 50 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E0 (Evolutionary Baseline)** | 0 / 21 | 1 / 21 | 3 / 21 | 4 / 21 | 106.0 | 3 / 21 |
| **E1 (Refined Evolutionary)** | 1 / 21 | 2 / 21 | 3 / 21 | 4 / 21 | 106.0 | 3 / 21 |
| **ES1 (Evolution + Proximity)** | 1 / 21 | 2 / 21 | 4 / 21 | 4 / 21 | 107.0 | 4 / 21 |
| **ES2 (Evolution + Acc + Prox)** | 1 / 21 | 4 / 21 | 4 / 21 | 5 / 21 | 103.0 | 4 / 21 |
| **ES3 (Structural-Prioritized)** | 4 / 21 | 5 / 21 | 5 / 21 | 7 / 21 | 92.0 | 5 / 21 |

---

## 3. Safeguard Against Overfitting
* **Free parameters tuned on benchmark**: **Zero**.
* All formulas and coefficients were pre-specified based on biological rationale prior to running the diagnostic scripts.
* No parameter was modified after inspecting benchmark outcomes.
* **All models are strictly eligible for independent validation.**

---

## 4. Prototype Recommendation

We recommend **Model ES3 (Structural-Prioritized Hybrid)** for further development and production integration.

### Rationale:
1. **Dramatic Performance Gain**: Recovers **5 / 21** hotspots in the Top 10% (a **5-fold increase** over the 1/21 baseline) and **7 / 21** in the Top 25% (recall: 33.33%).
2. **Median Rank Shift**: Improves the median hotspot rank from **106.0** (E0) down to **92.0** (ES3).
3. **Robustness**: Showcases stable and consistent improvement across all cutoffs (Top 5%, 10%, 20%, 25%).
4. **FASTA Compatibility**: Since it uses pre-computed reference structural properties (derived from crystal structure PDB 6EQE) projected using the existing mapper, it runs instantly from sequence input with zero runtime structure prediction overhead.
