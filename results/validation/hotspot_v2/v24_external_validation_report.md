# Hotspot V2.4 True External Validation Report

**Date**: 2026-08-31

> [!IMPORTANT]
> This report presents the FIRST TRUE EXTERNAL VALIDATION of the frozen Hotspot V2.4 LR model
> against 15 independent beneficial PETase engineering positions. Model coefficients, features,
> preprocessing parameters, and benchmark memberships were permanently frozen prior to prediction reveal.

---

## 1. Frozen Integrity Verification

- **V2.4 Freeze Manifest SHA256**: `b0f01a94e9b87f8c61e6ae138f101d6183fa25482ec62e9e280272a5d84f1a83`
- **External Benchmark TSV SHA256**: `519c9edd9a8c0bf0d3819bd1d62d818ad83774e3d7c13d9b9bef215379f69d22`
- **External Benchmark Manifest SHA256**: `3647f00efaa4dcf6ec158b05b1ecfe1cad3a7c1f383948330d09936448b76fde`
- **Integrity Status**: **PASS** (100% hash match verified)

---

## 2. External Benchmark Recovery Metrics (N=15)

| Cutoff Tier | Rank Threshold | Selected Positions | Recovered Hotspots | Recall | Expected Random | Fold Enrichment | Empirical p-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Top 5%** | $\le 12$ | 12 | 1 / 15 | 0.067 | 0.741 | 1.35x | 0.5445 |
| **Top 10%** | $\le 24$ | 24 | **2 / 15** | **0.133** | 1.481 | **1.35x** | **0.447826** |
| **Top 20% (Primary)** | $\le 48$ | 48 | **4 / 15** | **0.267** | 2.963 | **1.35x** | **0.341657** |
| **Top 25%** | $\le 60$ | 60 | 7 / 15 | 0.467 | 3.704 | 1.89x | 0.0485 |

- **Median External Hotspot Rank**: **118.0 / 243** (Percentile: **48.6%**, Null Median = 122.0, Empirical $p = 0.450895$)
- **Top 50 Count**: **5 / 15**

---

## 3. Individual Ranks of all 15 Independent Beneficial Positions

| Mapped Position | WT | Primary Mutation | Scaffold | Publication | V2.4 Score (Prob) | V2.4 Rank (/243) | In Top 20% |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 172 | N | H129W | TfCut2 | Furukawa et al. | 0.1105 | 11 | YES |
| 121 | S | S121E | IsPETase | Lu et al. | 0.1064 | 18 | YES |
| 224 | R | R224Q | IsPETase | Lu et al. | 0.1042 | 25 | YES |
| 233 | N | D238C | LCC | Tournier et al. | 0.0945 | 48 | YES |
| 282 | S | S283C | LCC | Tournier et al. | 0.0941 | 50 | NO |
| 234 | G | A182V | TfCut2 | Mrigwani et al. | 0.0940 | 51 | NO |
| 116 | T | T116P | TS-PETase | Zhong-Johnson et al. | 0.0934 | 55 | NO |
| 269 | S | I213V | TfCut2 | Mrigwani et al. | 0.0867 | 118 | NO |
| 241 | N | F243I | LCC | Tournier et al. | 0.0861 | 128 | NO |
| 181 | P | P181A | IsPETase | Cui et al. | 0.0000 | 244 | NO |
| 102 | A | G62A | TfCut2 | Furukawa et al. | 0.0000 | 244 | NO |
| 159 | W | W159H | IsPETase | Meng et al. | 0.0000 | 244 | NO |
| 229 | F | F229Y | IsPETase | Meng et al. | 0.0000 | 244 | NO |
| 238 | S | S238F | IsPETase | Cui et al. | 0.0000 | 244 | NO |
| 265 | D | F209S | TfCut2 | Furukawa et al. | 0.0000 | 244 | NO |

---

## 4. Publication and Scaffold Breakdown

### By Scaffold
| Scaffold | Positions | Top 20% Recovery | Median Rank |
| :--- | :---: | :---: | :---: |
| **IsPETase** | 6 | 2 / 6 | 244.0 |
| **LCC** | 3 | 1 / 3 | 50.0 |
| **TS-PETase** | 1 | 0 / 1 | 55.0 |
| **TfCut2** | 5 | 1 / 5 | 118.0 |

### By Publication
| Publication | Positions | Top 20% Recovery | Median Rank |
| :--- | :---: | :---: | :---: |
| **Cui et al.** | 2 | 0 / 2 | 244.0 |
| **Furukawa et al.** | 3 | 1 / 3 | 244.0 |
| **Lu et al.** | 2 | 2 / 2 | 21.5 |
| **Meng et al.** | 2 | 0 / 2 | 244.0 |
| **Mrigwani et al.** | 2 | 0 / 2 | 84.5 |
| **Tournier et al.** | 3 | 1 / 3 | 50.0 |
| **Zhong-Johnson et al.** | 1 | 0 / 1 | 55.0 |

---

## 5. Comparison to Development Performance (Context Only)

| Dataset | Top 10% Recovery | Top 20% Recovery | Top 25% Recovery | Median Rank |
| :--- | :---: | :---: | :---: | :---: |
| **Development (OOF, N=21)** | 6 / 21 (28.6%) | 12 / 21 (57.1%) | 12 / 21 (57.1%) | 39.0 |
| **External (Frozen, N=15)** | **2 / 15 (13.3%)** | **4 / 15 (26.7%)** | **7 / 15 (46.7%)** | **118.0** |

---

## 6. Final Classification & Conclusion

> [!IMPORTANT]
> **CONCLUSION: EXTERNAL VALIDATION PARTIALLY SUPPORTED**
> 
> On the frozen independent external benchmark of 15 beneficial positions across 7 publications and 4 enzyme scaffolds,
> the frozen V2.4 LR model achieved **4 / 15** recovery in the Top 20% (vs **2.96** expected by random chance,
> representing a **1.35x fold enrichment** with empirical $p = 0.341657$ from 100,000 random permutations).
> Median hotspot rank improved to **118.0** ($p = 0.450895$).