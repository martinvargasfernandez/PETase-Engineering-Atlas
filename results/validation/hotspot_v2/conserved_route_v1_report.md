# Hotspot Conserved Route V1 & Dual-Route Simulation Report

**Date**: 2026-08-31

---

## 1. Conserved Route V1 Performance (N=45 FVI=0 Universe)

| Model | Top 10% (4) | Top 20% (9) | Top 25% (11) | Median Rank | Top 10 Count | Top 20 p-value | Median p-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Diagnostic Baseline | - | 2 / 6 | - | 27.5 / 45 | - | - | - |
| **C-LR (OOF)** | 0 / 6 | 2 / 6 | 2 / 6 | 22.5 / 45 | 2 | 0.9365 | 0.9990 |
| **C-LR-BAL (OOF)** | **1 / 6** | **2 / 6** | **2 / 6** | **24.0 / 45** | **2** | **0.9390** | **1.0000** |

---

## 2. Learned Structural Coefficients for Conserved Route

| Feature | C-LR-BAL Mean Coef | Description |
| :--- | :---: | :--- |
| `distance_to_active_site_centroid` | -0.1071 |
| `normalized_B_factor` | -0.0725 |
| `degree` | +0.0691 |
| `packing_density` | +0.0691 |
| `betweenness_pctl` | +0.0653 |
| `closeness` | +0.0573 |
| `residue_depth` | +0.0525 |
| `long_range_density` | -0.0420 |
| `relative_SASA` | -0.0396 |
| `distance_to_substrate` | -0.0359 |
| `clustering` | +0.0340 |

---

## 3. Dual-Route Simulation (V2.4 + Conserved Route V1)

- **Route A (V2.4 Variable Top 20%)**: 48 positions
- **Route B (Conserved Structural Top 20%)**: 8 positions
- **Merged Shortlist Size**: **56 positions**
- **Total External Hotspots Recovered**: **6 / 15** (Recall: **0.400** vs V2.4 solo **4/15**)
- **Variable Hotspots Recovered (FVI>0)**: **4 / 9**
- **Conserved Hotspots Recovered (FVI=0)**: **2 / 6**

---

## 4. Decision & Recommendation

> [!NOTE]
> **RECOMMENDATION: KEEP CURRENT ARCHITECTURE**
> 
> Dual route simulation did not show sufficient improvement.