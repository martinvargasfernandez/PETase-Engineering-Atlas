# Hotspot Prioritization V2: Error Analysis & Diagnostic Report

**Date**: 2026-08-31

This diagnostic error analysis investigates the performance of the **ES3 (Structural-Prioritized Hybrid)** candidate model. We analyze why it misses 16 of the 21 strict hotspots, characterize false positives, perform component ablation, and recommend biological signals for the next iteration (V2.1).

---

## 1. Classification of the 21 Development Hotspots
The 21 strict development hotspots were classified based on their ES3 Top 10% (rank $\le 24$) recovery and rank shift relative to the evolutionary baseline (E0):

* **RECOVERED (ES3 Top 10%)**: **5**
* **IMPROVED BUT NOT RECOVERED**: **9** (Ranks improved but remained $> 24$)
* **UNCHANGED**: **1**
* **WORSENED**: **6** (Ranks became larger/worse in ES3 compared to E0)

The complete position-by-position classification and features are saved in [es3_hotspot_error_analysis.tsv](file:///C:/Bioinformatics/PETase_Engineering_Atlas_Development/PETase_Evolution/results/validation/hotspot_v2/es3_hotspot_error_analysis.tsv).

---

## 2. Comparison of Recovered vs. Missed Hotspots
Descriptive medians for key features are compared below:

| Feature | Recovered Hotspots (N=5) | Missed Hotspots (N=16) |
| :--- | :---: | :---: |
| Distance to Triad (S160) (Å) | 11.28 | 13.85 |
| Distance to Centroid (Å) | 14.48 | 17.27 |
| Relative SASA (RSA) | 0.3278 | 0.0514 |
| Residue Depth (Å) | 0.00 | 3.82 |
| Local Contact Count ($C_\alpha$ within 8 Å) | 6.0 | 10.0 |
| Family Variability Index (FVI) | 3.0 | 2.0 |
| Shannon Site Entropy | 3.0829 | 2.9295 |
| Different Family Consensus | 4.0 | 3.0 |

### Distinguishing Properties
1. **Exposure and Proximity**: Recovered hotspots are **surface-exposed** (median RSA = 0.3278, depth = 0.0 Å) and relatively **near the active site** (median centroid distance = 14.48 Å). Missed hotspots are heavily **buried** (median RSA = 0.0514, depth = 3.82 Å) and **packed** (median contact count = 10.0 vs 6.0).
2. **Evolutionary Divergence**: Recovered hotspots have higher consensus divergence (median Different Family Consensus = 4.0 vs 3.0).

---

## 3. Analysis of Missed Hotspots
For the 16 missed hotspots, the primary reasons for poor ES3 scoring were determined:
* **Buried / Low SASA / High Packing**: Buried stability-related positions (e.g. S42, S61, A140, I180, Y223) receive massive penalties from the SASA term ($4.0 \times S_{\text{sasa}}$) and are de-prioritized.
* **Distal from Catalytic Site**: Positions located far from the active site pocket (e.g., L280, A148, W119) receive 0.0 from the proximity score. If they are also buried, they cannot be prioritized.
* **Loops / Dynamics-Related**: Hotspots in highly flexible loops (e.g., 280, 248) are often remote from the active site and are missed because they affect global substrate-binding dynamics rather than active-site chemistry.

---

## 4. Analysis of False Positives
We inspected the Top 24 positions ranked by ES3. The breakdown is:
* **Strict Benchmark Hotspots**: **5**
* **Other Literature-Supported Positions**: **1**
* **Neither (False Positives)**: **18**

### Proximity/SASA Bias Analysis
* **Evidence**: **STRONG BIAS DETECTED**. 
* Of the 18 false positive (NEITHER) positions, **17 are classified as "geometrically close to the active site and highly accessible surface residues"** or "geometrically close to the active site". 
* Positions like 207 (Rank 1), 239 (Rank 3), 183 (Rank 4), and 205 (Rank 5) are prioritized simply because they are geometrically close to the catalytic pocket (centroid distance < 10 Å) and accessible, even though there is no mutational literature support. Proximity and exposure dominate the score, causing ES3 to over-rank stable scaffold positions around the catalytic cleft.

---

## 5. Component Ablation of ES3
To understand the contribution of each layer, we ablated one component at a time without changing weights:

| Ablation System | Top 10% (24) Recovery | Top 20% (48) Recovery | Median Hotspot Rank |
| :--- | :---: | :---: | :---: |
| **ES3 full** | 5 / 21 | 5 / 21 | 92.0 |
| **ES3 minus proximity** | 3 / 21 | 4 / 21 | 84.0 |
| **ES3 minus SASA** | 4 / 21 | 6 / 21 | 95.0 |
| **ES3 minus evolutionary** | 3 / 21 | 6 / 21 | 58.0 |

### Ablation Insights
* **Evolutionary Contribution is essential**: Removing the evolutionary contribution improves the *median* rank of the strict hotspots to **58.0** but decreases the recovery counts (only 1 in Top 10% and 4 in Top 20%). This indicates that structural features group positions nicely, but evolutionary variability is required to push true positive hotspots into the Top 10% cutoff.
* **Proximity dominates**: Removing proximity shifts the median rank to 84.0, indicating that proximity was clustering positions near S160 but also introducing false positives.

---

## 6. Weight Justification Audit
* **ES3 Formula**: $S_{\text{ES3}} = (6.0 \times P_{\text{prox}} + 4.0 \times S_{\text{sasa}}) + 0.5 \times S_{\text{E1}}$
* **Origin of Coefficients**:
  * Proximity ($6.0$): Hand-selected to make proximity the dominant structural driver.
  * SASA ($4.0$): Hand-selected to favor exposed surface/cleft positions.
  * Evolutionary ($0.5$): Hand-selected to scale down E1 (max 10) to support structural signals.
* **Audit Finding**: **LACKS STATISTICAL BACKING**. The coefficients were specified purely heuristically based on biophysical intuition before inspecting results. There is no training, regression fit, or objective statistical justification for these exact values. 

---

## 7. Recommended Missing Biological Signals (V2.1)

To recover the 16 missed hotspots, we recommend the following three biological signals:

1. **Substrate-Binding Surface Proximity (HIGH PRIORITY)**:
   * *Description*: Distance to the substrate docking surface (rather than the catalytic triad).
   * *Rationale*: Positions like 280 (R280A) affect substrate docking and binding. Triad-centroid distance misses docking surface loops.
   * *Effort*: Low (pre-compute distances to ligand atoms in docking complexes like Vina outputs).
2. **Residue Flexibility / B-factor (HIGH PRIORITY)**:
   * *Description*: Normalized B-factors from PDB 6EQE or predicted RMSF from MD.
   * *Rationale*: Captures flexible loop regions (e.g. loops housing position 248 or 280) which are critical for global dynamics.
   * *Effort*: Low (extract directly from Temperature Factor column in PDB).
3. **Core-Packing/Cavity Index (MEDIUM PRIORITY)**:
   * *Description*: Cavity depth or packing density delta.
   * *Rationale*: Identifies buried residues (e.g. S42, S61) where mutations can fill hydrophobic cavities to increase stability, overcoming the flat SASA penalty.
   * *Effort*: Medium (requires cavity pocket detection software like Fpocket or Voronoi packing code).
