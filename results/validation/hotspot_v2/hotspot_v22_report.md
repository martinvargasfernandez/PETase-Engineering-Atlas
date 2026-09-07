# Hotspot V2.2 Prototype Evaluation Report

**Date**: 2026-08-31

---

## 1. Missed Hotspot Classification (Step 1)

Of the 16 development hotspots missed by V21-B (rank > 24):

| Category | Count | Description |
| :--- | :---: | :--- |
| A: Buried/core-associated | 10 | SASA < 0.10, often deeply buried |
| B: Distal but flexible | 8 | Centroid distance > 15 Å, normalized B-factor > 0.50 |
| C: Distal and highly packed | 4 | Centroid distance > 15 Å, contacts ≥ 10 |
| D: Evolutionarily conserved | 12 | FVI ≤ 2 |
| E: Highly variable | 0 | FVI ≥ 5, diff_fam ≥ 5 |
| F: Unexplained | 0 | No category assigned |

> [!NOTE]
> Categories overlap: 10/16 are buried, 12/16 are conserved.
> The dominant failure mode is **buried + conserved** positions.

---

## 2. Residue Contact Network (Step 2)

- **Residues**: 265
- **Edges**: 1426
- **Cutoff**: 8.0 Å (Cα-Cα)
- **Long-range threshold**: sequence separation ≥ 12

Graph metrics computed without NetworkX (custom BFS/Brandes implementation).

---

## 3. Pre-Specified Model Formulas (Frozen Before Evaluation)

### V22-A: V21-B + Contact-Network Context
```
V22-A = mean(E_norm, P_sub, F_flex, Exposure, Betweenness_pctl, LongRange_density)
```

### V22-B: V21-B + Stability/Core Context
```
V22-B = mean(E_norm, P_sub, F_flex, Exposure, BuriedPolar, Underpacking, ChemMismatch)
```

### V22-C: V21-B + Evolutionary-Structure Interactions
```
V22-C = mean(E_norm, P_sub, F_flex, Exposure, BuriedVariable, CentralVariable, DistalVariable)
```

### V22-D: Multi-Route Maximum Support
```
Route 1 (Substrate):   mean(P_sub, Exposure, ContactsSubstrate_norm)
Route 2 (Flexibility): mean(F_flex, ContactsFlexible_norm, Exposure)
Route 3 (Buried):      mean(NormalizedBurial, BuriedVariable, BuriedDivergent, Underpacking, ChemMismatch)
Route 4 (Evolution):   mean(E_norm, FamilyDivergence, EntropyNorm)

V22-D = max(Route1, Route2, Route3, Route4)
```

---

## 4. Development Evaluation Results

| Model | Top10% (/21) | Top20% (/21) | Top25% (/21) | Median Rank | Top50 | FPs (Top24) | Proximal FPs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E0** | 1 | 3 | 4 | 106.0 | 3 | 23 | 0 |
| **ES3** | 5 | 5 | 7 | 92.0 | 5 | 19 | 7 |
| **V21-B** | 5 | 8 | 9 | 72.0 | 8 | 19 | 1 |
| **V22-A** | 3 | 4 | 8 | 71.0 | 5 | 21 | 1 |
| **V22-B** | 5 | 7 | 8 | 116.0 | 7 | 19 | 0 |
| **V22-C** | 1 | 5 | 8 | 86.0 | 6 | 23 | 0 |
| **V22-D** | 2 | 5 | 6 | 96.0 | 5 | 22 | 0 |

---

## 5. Trade-Off Analysis (Step 8)

### V22-A
- V21-B Top10 retained: **2/5** (187, 280)
- Rescued: **1** (186)
- Lost: **3** (117, 188, 212)
- Proximal FPs in Top24: 1

### V22-B
- V21-B Top10 retained: **2/5** (117, 212)
- Rescued: **3** (42, 186, 214)
- Lost: **3** (187, 188, 280)
- Proximal FPs in Top24: 0

### V22-C
- V21-B Top10 retained: **1/5** (280)
- Rescued: **0** (none)
- Lost: **4** (117, 187, 188, 212)
- Proximal FPs in Top24: 0

### V22-D
- V21-B Top10 retained: **1/5** (280)
- Rescued: **1** (140)
- Lost: **4** (117, 187, 188, 212)
- Proximal FPs in Top24: 0

---

## 6. V22-D Route Analysis

| Position | Residue | V22-D Rank | In Top10 | R1:Substrate | R2:Flex | R3:Buried | R4:Evo | Dominant Route |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 42 | S | 95 | NO | 0.268 | 0.552 | 0.432 | 0.595 | Route4:Evolution |
| 61 | S | 111 | NO | 0.336 | 0.484 | 0.000 | 0.566 | Route4:Evolution |
| 77 | T | 143 | NO | 0.300 | 0.509 | 0.149 | 0.283 | Route2:Flexibility |
| 95 | K | 140 | NO | 0.277 | 0.333 | 0.000 | 0.514 | Route4:Evolution |
| 117 | L | 75 | NO | 0.528 | 0.387 | 0.200 | 0.632 | Route4:Evolution |
| 119 | Q | 142 | NO | 0.509 | 0.370 | 0.000 | 0.283 | Route1:Substrate |
| 140 | T | 15 | YES | 0.200 | 0.759 | 0.079 | 0.388 | Route2:Flexibility |
| 148 | K | 88 | NO | 0.259 | 0.605 | 0.215 | 0.246 | Route2:Flexibility |
| 165 | G | 136 | NO | 0.522 | 0.143 | 0.146 | 0.268 | Route1:Substrate |
| 166 | S | 180 | NO | 0.416 | 0.068 | 0.256 | 0.309 | Route1:Substrate |
| 168 | I | 99 | NO | 0.547 | 0.251 | 0.273 | 0.589 | Route4:Evolution |
| 180 | A | 228 | NO | 0.162 | 0.093 | 0.313 | 0.312 | Route3:Buried |
| 186 | D | 96 | NO | 0.534 | 0.594 | 0.195 | 0.486 | Route2:Flexibility |
| 187 | S | 34 | NO | 0.528 | 0.715 | 0.000 | 0.597 | Route2:Flexibility |
| 188 | S | 26 | NO | 0.408 | 0.727 | 0.000 | 0.587 | Route2:Flexibility |
| 208 | I | 112 | NO | 0.546 | 0.564 | 0.000 | 0.242 | Route2:Flexibility |
| 212 | N | 33 | NO | 0.355 | 0.625 | 0.143 | 0.718 | Route4:Evolution |
| 214 | S | 82 | NO | 0.425 | 0.615 | 0.317 | 0.387 | Route2:Flexibility |
| 223 | S | 55 | NO | 0.241 | 0.674 | 0.000 | 0.462 | Route2:Flexibility |
| 248 | A | 121 | NO | 0.339 | 0.379 | 0.321 | 0.549 | Route4:Evolution |
| 280 | R | 8 | YES | 0.587 | 0.642 | 0.000 | 0.852 | Route4:Evolution |

---

## 7. Decision (Step 9)

**V21-B baseline**: Top10=5/21, Top20=8/21, Top25=9/21, Median=72.0

> [!NOTE]
> No V2.2 candidate meaningfully improves over V21-B without fitted weights.
> **RECOMMENDATION: KEEP V21-B** as the current development prototype.

---

## 8. Methodological Notes

- All model formulas were pre-specified and frozen BEFORE loading benchmark labels.
- No literature evidence (Known_mutations, Mutation_evidence) was used as a predictor feature.
- No weights were optimized against the 21 development hotspots.
- Contact network uses standard Cα-Cα 8.0 Å cutoff.
- Graph metrics computed via custom BFS/Brandes (NetworkX not available).
- All components normalized to 0-1 scales.
- V22-D uses maximum route support (max of 4 independent route scores).