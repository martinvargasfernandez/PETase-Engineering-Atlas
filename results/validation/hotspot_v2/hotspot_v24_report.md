# Hotspot V2.4 Interpretable Data-Driven Prototype Report

**Date**: 2026-08-31

> [!IMPORTANT]
> This is a DEVELOPMENT ONLY analysis. The 21 hotspot positions have been used
> extensively during model development and MUST NOT be presented as independent
> validation. Absence from the positive benchmark does NOT prove a position
> cannot be beneficial.

---

## 1. Development Dataset

- **Eligible positions**: 243
- **Positive hotspots**: 21 (development labels)
- **Features**: 12 pre-specified predictors
- **Regularization**: C = 1.0 (fixed, not tuned)
- **CV strategy**: Leave-one-positive-out (21 folds)

### Features Used

- `fvi`
- `shannon_entropy`
- `different_family_consensus`
- `global_conservation`
- `relative_SASA`
- `residue_depth`
- `distance_to_substrate`
- `distance_to_active_site_centroid`
- `normalized_B_factor`
- `packing_density`
- `long_range_density`
- `betweenness_pctl`

### Features Explicitly Excluded

- `Known_mutations` (literature evidence)
- `Mutation_evidence` (literature evidence)
- `literature_score` (literature evidence)
- `known_mutation_support` (literature evidence)
- `mutation_evidence_score` (literature evidence)

---

## 2. Model Comparison (Out-of-Fold Predictions)

| Model | Top10% (/21) | Top20% (/21) | Top25% (/21) | Median Rank | Top50 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **E0** | 1 | 3 | 4 | 106.0 | 3 |
| **V21-B** | 5 | 8 | 9 | 72.0 | 8 |
| **LR (OOF)** | 6 | 12 | 12 | 39.0 | 12 |
| **LR-BAL (OOF)** | 6 | 12 | 12 | 40.0 | 12 |

---

## 3. Learned Coefficients

| Feature | LR Mean Coef | LR Sign Stability | LR-BAL Mean Coef | LR-BAL Sign Stability |
| :--- | :---: | :---: | :---: | :---: |
| `residue_depth` | -0.0422 | 1.00 | -0.0921 | 1.00 |
| `relative_SASA` | +0.0391 | 1.00 | +0.0917 | 1.00 |
| `distance_to_substrate` | -0.0315 | 1.00 | -0.0815 | 1.00 |
| `normalized_B_factor` | +0.0326 | 1.00 | +0.0806 | 1.00 |
| `distance_to_active_site_centroid` | -0.0247 | 1.00 | -0.0571 | 1.00 |
| `shannon_entropy` | +0.0160 | 1.00 | +0.0367 | 1.00 |
| `fvi` | -0.0071 | 1.00 | -0.0284 | 1.00 |
| `different_family_consensus` | -0.0071 | 1.00 | -0.0284 | 1.00 |
| `betweenness_pctl` | -0.0150 | 1.00 | -0.0253 | 1.00 |
| `packing_density` | +0.0025 | 0.81 | +0.0251 | 1.00 |
| `global_conservation` | -0.0117 | 1.00 | -0.0245 | 1.00 |
| `long_range_density` | -0.0057 | 1.00 | -0.0054 | 0.76 |

### Biological Interpretability

- **`residue_depth`**: -0.0921 — NEGATIVE (lower → more likely hotspot)
- **`relative_SASA`**: +0.0917 — POSITIVE (higher → more likely hotspot)
- **`distance_to_substrate`**: -0.0815 — NEGATIVE (lower → more likely hotspot)
- **`normalized_B_factor`**: +0.0806 — POSITIVE (higher → more likely hotspot)
- **`distance_to_active_site_centroid`**: -0.0571 — NEGATIVE (lower → more likely hotspot)

---

## 4. Permutation Control (N=1,000)

| Model | Metric | Observed | Null Mean ± SD | Empirical p |
| :--- | :--- | :---: | :---: | :---: |
| LR | top10_recovery | 6 | 4.36 ± 1.44 | 0.2178 |
| LR | top20_recovery | 12 | 7.49 ± 1.56 | **0.0050** |
| LR | median_rank | 39.0 | 77.22 ± 15.29 | **0.0050** |
| LR-BAL | top10_recovery | 6 | 4.45 ± 1.52 | 0.2478 |
| LR-BAL | top20_recovery | 12 | 7.72 ± 1.61 | **0.0100** |
| LR-BAL | median_rank | 40.0 | 74.39 ± 14.9 | **0.0110** |

---

## 5. Leakage Audit

- ✅ No literature evidence columns in feature set
- ✅ Held-out hotspot excluded from its training fold
- ✅ Feature standardization fitted INSIDE each fold
- ✅ No benchmark labels used for feature engineering
- ✅ Production files untouched
- ✅ Model parameters (C=1.0) fixed before evaluation

---

## 6. Decision

**V21-B**: Top10=5/21, Top20=8/21, Top25=9/21, Median=72.0
**LR (OOF)**: Top10=6/21, Top20=12/21, Top25=12/21, Median=39.0
**LR-BAL (OOF)**: Top10=6/21, Top20=12/21, Top25=12/21, Median=40.0

> [!IMPORTANT]
> **RECOMMENDATION: ADVANCE LR** for independent validation.
> Out-of-fold performance exceeds V21-B with significant permutation p-values.


## 7. Methodological Notes

- Logistic regression implemented from scratch (no scikit-learn dependency).
- L2 regularization with fixed C=1.0.
- 1000 label permutations with seed=42.
- Leave-one-positive-out CV: each hotspot predicted by a model that never saw it.
- Background positions: mean prediction across all 21 folds.
- Class-balanced model uses inverse-frequency weighting.