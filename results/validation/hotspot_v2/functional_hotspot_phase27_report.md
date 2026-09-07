# Phase 27 — Function-First Shortlist Prioritization & Baseline Audit Report

**Date**: 2026-09-01

---

## 1. Resolution of V2.4 Baseline Discrepancy

- **Audit Finding**: In Phase 15, V2.4 Top 20% recovery was reported as 4/15 based on a Top 20% cutoff size of 48 positions out of 243 universe positions (which captured position 233 at rank 48). When evaluated on the **exact Top 20 positions**, V2.4 recovers **2 / 15 (13.3%)** (positions 172 and 121).
- **Canonical V2.4 Baseline Ranks**:
  - V2.4 Top 15 positions: **1 / 15** (6.7%)
  - V2.4 Top 20 positions: **2 / 15** (13.3%)
  - V2.4 Top 24 positions: **2 / 15** (13.3%)
  - V2.4 Top 30 positions: **3 / 15** (20.0%)
  - V2.4 Top 48 positions (Top 20% of 243 universe): **4 / 15** (26.7%)

---

## 2. Function-First Shortlist Performance (Primary Cutoff: Top 20)

| Shortlist Cutoff | Cutoff Size (N) | Hotspots Recovered | Recall | Expected Random | Fold Enrichment | Permutation p-value | FVI=0 Conserved Recovered |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Top 15` | 15 | **2 / 15** | 13.3% | 0.85 | **2.34x** | **p = 0.20603** | **2 / 6** |
| `Top 20` **(PRIMARY)** | 20 | **2 / 15** | 13.3% | 1.14 | **1.75x** | **p = 0.31955** | **2 / 6** |
| `Top 24` | 24 | **3 / 15** | 20.0% | 1.37 | **2.19x** | **p = 0.14485** | **2 / 6** |
| `Top 30` | 30 | **5 / 15** | 33.3% | 1.71 | **2.92x** | **p = 0.01798** | **2 / 6** |

---

## 3. Direct Comparison: V2.4 Baseline vs. Function-First Shortlists

| Shortlist Size | V2.4 Hotspots Recovered | Function-First Hotspots Recovered | V2.4 Recall | Function-First Recall | Function-First Enrichment | Function-First p-value |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Top 15** | 1 / 15 | **2 / 15** | 6.7% | **13.3%** | **2.34x** | **p = 0.20603** |
| **Top 20 (PRIMARY)** | 2 / 15 | **2 / 15** | 13.3% | **13.3%** | **1.75x** | **p = 0.31955** |
| **Top 24** | 2 / 15 | **3 / 15** | 13.3% | **20.0%** | **2.19x** | **p = 0.14485** |

---

## 4. Decision & Next Steps

### Final Decision: **B. FUNCTIONAL LAYER WORKS BUT SHORTLIST PRIORITIZATION INCONCLUSIVE**
