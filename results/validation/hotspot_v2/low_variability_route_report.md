# Low-Variability Hotspot Route (Phase 19) Report

**Date**: 2026-08-31

---

## 1. Low-Variability Route Performance (N=14 Hotspots, Universe N=179)

| Model | Top 10% | Top 20% | Top 25% | Median Rank | Top 50 Count | Top 20 p-value | Median p-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Structural Baseline | 1 / 14 | 4 / 14 | 4 / 14 | 72.0 | 4 | - | - |
| **LV-LR (OOF)** | 1 / 14 | 3 / 14 | 3 / 14 | 94.0 | 3 | 0.9865 | 0.9960 |
| **LV-LR-BAL (OOF)** | **1 / 14** | **2 / 14** | **3 / 14** | **83.0** | **3** | **0.9990** | **0.9905** |

---

## 2. Learned Structural Coefficients

| Feature | LV-LR-BAL Mean Coef | Sign Stability |
| :--- | :---: | :---: |
| `distance_to_active_site_centroid` | -0.1090 | 100% |
| `distance_to_substrate` | -0.0613 | 100% |
| `relative_SASA` | -0.0490 | 100% |
| `degree` | +0.0356 | 100% |
| `packing_density` | +0.0356 | 100% |
| `residue_depth` | +0.0309 | 100% |
| `betweenness_pctl` | +0.0200 | 100% |
| `closeness` | -0.0187 | 100% |
| `normalized_B_factor` | -0.0141 | 100% |
| `clustering` | +0.0135 | 100% |
| `long_range_density` | +0.0091 | 100% |

---

## 3. Dual-Route Simulation Results

- **Merged Shortlist Size**: **55 positions**
- **Total External Hotspots Recovered**: **6 / 19** (Recall: **0.316**)
- **Variable Hotspots (FVI>=3)**: **3 / 5**
- **Low-Variability Hotspots (FVI<=2)**: **3 / 14**

---

## 4. Decision & Recommendation

> [!NOTE]
> **RECOMMENDATION: STRUCTURAL FEATURES INSUFFICIENT FOR LOW-VARIABILITY HOTSPOTS**
> 
> Supervised structural models (LV-LR/LV-LR-BAL) on static features do not beat the simple parameter-free structural baseline or achieve $p < 0.05$ significance.
> Capturing low-variability hotspots reliably will require molecular dynamics simulation descriptors, ligand docking energetics, or deep learning embeddings.