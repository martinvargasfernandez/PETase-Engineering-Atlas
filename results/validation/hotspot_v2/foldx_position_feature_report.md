# FoldX Low-Variability Position-Level Energetic Feature & Benchmark Report

**Date**: 2026-09-01

---

## 1. Frozen Input Verification

- **Mutation Matrix Path**: `results\validation\hotspot_v2\foldx_low_variability_mutation_matrix.tsv`
- **Mutation Matrix SHA256**: `b9feff9aab5e5d6f3703096ea7bf6bdb16f6dde405de032fb66d89abf2976fa3` (Verified match)
- **Position Feature Table SHA256**: `6104fea35c4d756dd71405a0d97564998fdd96fce8c28ef0627c5142f15bbe6d` (Frozen)
- **Evaluated Low-Variability Universe**: **179 resolved positions** (14 beneficial hotspots, 165 background positions)

---

## 2. Pre-Defined Energetic Feature Benchmark Results

| Feature | Order | Hotspot Median | Background Median | Effect Direction | Mann-Whitney U | Raw p-value | FDR q-value | Significant (q < 0.05) | Top 20% Recovery | Median Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `ddg_min` | ASCENDING | -0.2159 | -0.3317 | HOTSPOT_HIGHER | 1108.0 | 0.4014 | 0.7406 | **NO** | 4 / 14 | 95.0 / 179 |
| `ddg_mean` | ASCENDING | 4.0411 | 3.2994 | HOTSPOT_HIGHER | 1173.0 | 0.5396 | 0.7406 | **NO** | 4 / 14 | 106.0 / 179 |
| `ddg_median` | ASCENDING | 3.6274 | 2.8232 | HOTSPOT_HIGHER | 1210.0 | 0.6172 | 0.7406 | **NO** | 3 / 14 | 116.0 / 179 |
| `fraction_stabilizing` | DESCENDING | 0.0000 | 0.0000 | HOTSPOT_LOWER | 1281.0 | 0.2256 | 0.7406 | **NO** | 5 / 14 | 114.0 / 179 |
| `fraction_neutral` | DESCENDING | 0.0790 | 0.1053 | HOTSPOT_LOWER | 993.5 | 0.8113 | 0.8113 | **NO** | 2 / 14 | 105.5 / 179 |
| `fraction_destabilizing` | ASCENDING | 0.8441 | 0.8750 | HOTSPOT_LOWER | 1182.5 | 0.5602 | 0.7406 | **NO** | 3 / 14 | 88.5 / 179 |

---

## 3. Evaluation of Specific Beneficial Mutations (WHAT-to-Mutate)

| Position | Target Beneficial Mutation | FoldX $\Delta\Delta G$ (kcal/mol) | Classification |
| :---: | :---: | :---: | :---: |
| 102 | A | +nan | DESTABILIZING |
| 116 | P | -0.6964 | YES |
| 133 | F | -0.0597 | NEUTRAL |
| 159 | H | +4.6926 | DESTABILIZING |
| 181 | A | +10.8065 | DESTABILIZING |
| 200 | A | +7.8317 | DESTABILIZING |
| 229 | Y | +4.3355 | DESTABILIZING |
| 234 | V | +2.6564 | DESTABILIZING |
| 238 | F | +1.0822 | DESTABILIZING |
| 241 | I | +2.3064 | DESTABILIZING |
| 260 | C | +nan | DESTABILIZING |
| 265 | S | +3.2730 | DESTABILIZING |
| 281 | P | +8.6068 | DESTABILIZING |
| 282 | C | +3.9173 | DESTABILIZING |

---

## 4. Conclusion & Decision

### Final Decision: **C. ENERGETIC SIGNAL INSUFFICIENT**
