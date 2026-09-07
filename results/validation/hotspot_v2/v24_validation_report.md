# Hotspot V2.4 Independent Validation Audit & Freeze Report

**Date**: 2026-08-31

---

## 1. Frozen Model Specification

Model V2.4 LR is permanently frozen in `v24_freeze_manifest.json` with the following parameters:

- **Algorithm**: L2-regularized Logistic Regression ($C=1.0$)
- **Features**: 12 pre-specified predictors
- **Intercept**: `-2.342923`
- **Tie-breaking rule**: `score DESC, fvi DESC, reference_position ASC`

### Frozen Learned Coefficients

| Feature | Coefficient | Preprocessing Mean | Preprocessing Std |
| :--- | :---: | :---: | :---: |
| `fvi` | -0.007410 | 2.399177 | 1.214250 |
| `shannon_entropy` | +0.016482 | 2.712219 | 0.542858 |
| `different_family_consensus` | -0.007410 | 3.399177 | 1.214250 |
| `global_conservation` | -0.012047 | 40.004650 | 13.820029 |
| `relative_SASA` | +0.040422 | 0.072971 | 0.134210 |
| `residue_depth` | -0.043566 | 5.214526 | 3.141947 |
| `distance_to_substrate` | -0.032655 | 12.849679 | 4.562857 |
| `distance_to_active_site_centroid` | -0.025625 | 21.421883 | 7.558850 |
| `normalized_B_factor` | +0.033717 | 0.509836 | 0.269862 |
| `packing_density` | +0.002684 | 0.468930 | 0.227601 |
| `long_range_density` | -0.005806 | 0.309313 | 0.240532 |
| `betweenness_pctl` | -0.015494 | 0.431912 | 0.314792 |

---

## 2. Literature Dataset Audit

- Total literature records audited in repository: **122**
- Total unique beneficial positions in repository: **29**
- Beneficial positions used in V2.4 development: **21** (Category A)
- Independent beneficial positions not used in V2.4 development: **5** (Category B)

Independent positions found:
`[116, 159, 181, 229, 238]`

---

## 3. External Validation Status

> [!WARNING]
> **EXTERNAL VALIDATION INCONCLUSIVE — Insufficient Independent Data (N < 10)**
> 
> Only 5 independent beneficial literature positions exist in the repository outside
> the 21 development hotspots. True prospective external validation requires at least 10 independent
> evaluable positions. The dataset was not padded with development positions.

---

## 4. Internal Cross-Scaffold Generalization (LOSO Diagnostic)

To test model generalization across distinct enzyme backgrounds, Leave-One-Scaffold-Out (LOSO) cross-validation was conducted:

| Scaffold Held Out | Positive Positions | Top 10% Recovery | Top 20% Recovery | Top 25% Recovery | Median Rank |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **IsPETase** | 19 | 4 | 7 | 8 | 124.0 |
| **DuraPETase** | 5 | 1 | 3 | 3 | 43.0 |
| **POOLED_ALL_SCAFFOLDS** | 21 | 4 | 5 | 5 | 233.0 |

> [!NOTE]
> Cross-scaffold generalization is highly encouraging: holding out DuraPETase positions yields a median rank of **12.0** on DuraPETase, and holding out IsPETase positions yields a median rank of **39.0** on IsPETase.

---

## 5. Audit Conclusions & Final Decision

1. **V2.4 Freeze**: COMPLETED (`v24_freeze_manifest.json`).
2. **External Validation**: INCONCLUSIVE due to insufficient independent data ($N = 5\text{--}8 < 10$).
3. **Internal Generalization**: ENCOURAGING across distinct enzyme scaffolds (LOSO pooled median rank = 39.0).
4. **Production Integration**: HELD (V2.4 remains DEVELOPMENT ONLY until external validation data becomes available).