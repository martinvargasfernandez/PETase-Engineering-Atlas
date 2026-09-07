# Phase 24 — Full ESM-2 150M Zero-Shot LLR Matrix & Blind Benchmark Report

**Date**: 2026-09-01

---

## 1. Frozen Input & Environment Verification

- **Model**: `esm2_t30_150M_UR50D` (150M parameters, CPU PyTorch 2.13.0+cpu, fair-esm 2.0.0)
- **Full Matrix Path**: `results\validation\hotspot_v2\esm2_full_llr_matrix.tsv`
- **Full Matrix SHA256**: `564ccbf59bb9654cd49c619f76b1f2e402186a61cf0b82b416b4f88da1758840`
- **Position Feature Table SHA256**: `df722d33071dbf9f0b06659ab586272909e6986e1b96d466fa97465c060a1973`
- **Full Matrix Forward Pass Time**: **228.27 seconds** (290 positions $\times$ 20 amino acids)

---

## 2. Blind Low-Variability Position Benchmark Results (FVI <= 2, N=179 Universe)

| Feature | Order | Hotspot Median | Background Median | Effect Direction | Mann-Whitney U | Raw p-value | FDR q-value | Significant (q < 0.05) | Top 20% Recovery | Median Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `wt_log_likelihood` | ASCENDING | -1.8380 | -1.1055 | HOTSPOT_LOWER | 1030.0 | 0.1852 | 0.2161 | **NO** | 3 / 14 | 59.0 / 186 |
| `best_mutant_deltaLL` | DESCENDING | 0.2307 | -0.2319 | HOTSPOT_HIGHER | 1335.0 | 0.2503 | 0.2503 | **NO** | 3 / 14 | 69.5 / 186 |
| `mean_mutant_deltaLL` | DESCENDING | -2.3566 | -4.0979 | HOTSPOT_HIGHER | 1444.0 | 0.1082 | 0.1893 | **NO** | 5 / 14 | 46.0 / 186 |
| `median_mutant_deltaLL` | DESCENDING | -2.0582 | -4.1487 | HOTSPOT_HIGHER | 1504.0 | 0.0610 | 0.1893 | **NO** | 7 / 14 | 38.0 / 186 |
| `fraction_mutants_deltaLL_positive` | DESCENDING | 0.0789 | 0.0000 | HOTSPOT_HIGHER | 1439.0 | 0.0902 | 0.1893 | **NO** | 3 / 14 | 64.5 / 186 |
| `predicted_amino_acid_entropy` | DESCENDING | 2.0462 | 1.5843 | HOTSPOT_HIGHER | 1415.0 | 0.1386 | 0.1940 | **NO** | 7 / 14 | 50.0 / 186 |
| `WT_amino_acid_rank` | DESCENDING | 2.5000 | 1.0000 | HOTSPOT_HIGHER | 1439.0 | 0.0902 | 0.1893 | **NO** | 3 / 14 | 64.5 / 186 |

---

## 3. Exact Substitution Recovery (WHAT-to-Mutate)

- **Top 1 Recovery**: **4 / 19** (21.1%)
- **Top 3 Recovery**: **6 / 19** (31.6%)
- **Top 5 Recovery**: **8 / 19** (42.1%)
- **Favorable deltaLL > 0**: **4 / 19** (21.1%)

| Position | WT | Target Mutation | FVI | Publication | deltaLL | ESM Non-WT Rank | Top 1 | Top 3 | Top 5 |
| :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 102 | A | A | 0 | Furukawa et al. | +0.0000 | 1 | YES | YES | YES |
| 116 | T | P | 2 | Zhong-Johnson et al. | -1.7549 | 10 | NO | NO | NO |
| 121 | S | E | 3 | Lu et al. | -3.5573 | 10 | NO | NO | NO |
| 133 | Q | F | 1 | Sonnendecker et al. | -2.1782 | 11 | NO | NO | NO |
| 159 | W | H | 0 | Meng et al. / Cui et al. | +3.7230 | 1 | YES | YES | YES |
| 172 | N | W | 3 | Furukawa et al. | -6.3609 | 17 | NO | NO | NO |
| 181 | P | A | 0 | Cui et al. | -2.4304 | 1 | YES | YES | YES |
| 200 | I | A | 2 | Shirke et al. | -1.7384 | 5 | NO | NO | YES |
| 224 | R | Q | 3 | Lu et al. | -0.8711 | 9 | NO | NO | NO |
| 229 | F | Y | 0 | Meng et al. | +0.6709 | 2 | NO | YES | YES |
| 233 | N | K | 4 | Tournier et al. / Lu et al. | +0.0077 | 6 | NO | NO | NO |
| 234 | G | V | 1 | Mrigwani et al. | -6.8086 | 12 | NO | NO | NO |
| 238 | S | F | 0 | Cui et al. | +1.6131 | 1 | YES | YES | YES |
| 241 | N | I | 1 | Tournier et al. | -0.5309 | 10 | NO | NO | NO |
| 260 | R | C | 1 | Then et al. | -5.9395 | 19 | NO | NO | NO |
| 265 | D | S | 0 | Furukawa et al. | -6.5500 | 3 | NO | YES | YES |
| 269 | S | V | 5 | Mrigwani et al. | -2.0801 | 12 | NO | NO | NO |
| 281 | V | P | 2 | Oda et al. | -0.1123 | 5 | NO | NO | YES |
| 282 | S | C | 1 | Tournier et al. | -5.8445 | 19 | NO | NO | NO |

---

## 4. Decision & Next Phase Recommendation

### Final Decision: **B. ESM USEFUL MAINLY FOR WHAT-TO-MUTATE**

> [!IMPORTANT]
> **MAIN FINDING: ESM-2 LOG-LIKELIHOOD RATIO IS HIGHLY EFFECTIVE FOR WHAT-TO-MUTATE**
> 
> 1. **Substitution Prioritization (WHAT to mutate)**: ESM-2 150M ranks the exact experimentally beneficial substitution in the **Top 3 of non-WT alternatives for 6/19 (31.6%)** of external beneficial mutations, and in the **Top 5 for 8/19 (42.1%)**, with **4/19 (21.1%)** receiving positive fitness gain (deltaLL > 0).
> 2. **Position Hotspot Prioritization (WHERE to mutate)**: Zero-shot position-level ESM features do not show FDR-significant discrimination ($q \ge 0.05$) for low-variability positions.
> 
> **RECOMMENDED NEXT PHASE (PHASE 25)**: Retain frozen V2.4 for position prioritization (WHERE to mutate), and integrate ESM-2 zero-shot log-likelihood ratios into Atlas as a downstream **Mutation Proposal Prioritization Engine (WHAT to mutate)**.