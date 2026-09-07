# Hotspot V2.3 Multi-Route Prioritization Report

**Date**: 2026-08-31

---

## 1. Route Definitions (Frozen Before Evaluation)

### Route A — Substrate / Interface
```
Route_A = mean(substrate_proximity, contacts_substrate_norm, relative_SASA, normalized_B_factor)
```
Purpose: positions affecting substrate recognition, docking, or pocket geometry.

### Route B — Flexibility / Dynamics
```
Route_B = mean(normalized_B_factor, (1 - packing_density), contacts_flexible_norm, loop_indicator)
```
Purpose: structurally mobile or conformationally permissive regions.

### Route C — Stability / Core
```
Route_C = mean(normalized_burial, packing_density, long_range_density, betweenness_pctl, hydrophobic_env)
```
Purpose: buried or scaffold positions relevant to stability engineering.

### Route D — Evolutionary
```
Route_D = mean(fvi_norm, entropy_norm, family_divergence)
```
Purpose: positions with independent evolutionary evidence for tolerated variation.

---

## 2. Primary Shortlist: Top 6 Per Route

- **Unique positions selected**: 23
- **Hotspots recovered**: 4/21
- **Recall**: 0.190

### Comparison

| Method | Positions Selected | Hotspots Recovered | Recall |
| :--- | :---: | :---: | :---: |
| E0 Top10% | 24 | 1/21 | 0.048 |
| V21-B Top10% | 24 | 5/21 | 0.238 |
| **V2.3 Multi-Route (Top6×4)** | **23** | **4/21** | **0.190** |
| V2.3 Interleaved-24 | 24 | 4/21 | 0.190 |

### Sensitivity to Shortlist Size

| Top N per Route | Unique Positions | Hotspots Recovered | Recall |
| :---: | :---: | :---: | :---: |
| 4 | 16 | 2/21 | 0.095 |
| **6 (primary)** | **23** | **4/21** | **0.190** |
| 8 | 30 | 5/21 | 0.238 |
| 10 | 35 | 6/21 | 0.286 |

---

## 3. Route Contributions

| Route | Top6 Hotspots | Positions | Unique Recoveries |
| :--- | :---: | :--- | :---: |
| Route_A | 1 | 280 | 1 |
| Route_B | 2 | 140,188 | 2 |
| Route_C | 1 | 180 | 1 |
| Route_D | 0 | none | 0 |

- **Hotspots supported by >1 route**: 0 ()

---

## 4. Primary Shortlist Details

| Position | Residue | Hotspot | Routes | Strongest | A Rank | B Rank | C Rank | D Rank | V21-B Rank |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 2 | N | NO | Route_D | Route_D | 193 | 77 | 200 | 1 | 67 |
| 9 | L | NO | Route_D | Route_D | 194 | 78 | 201 | 3 | 69 |
| 54 | S | NO | Route_D | Route_D | 164 | 131 | 141 | 4 | 36 |
| 80 | A | NO | Route_C | Route_C | 180 | 237 | 5 | 139 | 230 |
| 82 | A | NO | Route_C | Route_C | 188 | 238 | 3 | 211 | 236 |
| 87 | Y | NO | Route_A | Route_A | 4 | 116 | 109 | 129 | 66 |
| 136 | S | NO | Route_D | Route_D | 67 | 104 | 192 | 2 | 11 |
| 140 | T | YES | Route_B | Route_B | 101 | 1 | 193 | 121 | 105 |
| 143 | S | NO | Route_B | Route_B | 128 | 2 | 180 | 228 | 123 |
| 146 | Y | NO | Route_B | Route_B | 135 | 4 | 115 | 115 | 173 |
| 172 | N | NO | Route_A | Route_A | 5 | 146 | 198 | 69 | 13 |
| 179 | A | NO | Route_C | Route_C | 223 | 236 | 4 | 213 | 235 |
| 180 | A | YES | Route_C | Route_C | 242 | 150 | 1 | 169 | 242 |
| 183 | A | NO | Route_C | Route_C | 64 | 136 | 6 | 82 | 176 |
| 188 | S | YES | Route_B | Route_B | 28 | 5 | 239 | 55 | 9 |
| 189 | T | NO | Route_B | Route_B | 41 | 6 | 97 | 49 | 33 |
| 192 | S | NO | Route_B | Route_B | 70 | 3 | 151 | 61 | 41 |
| 201 | F | NO | Route_C | Route_C | 221 | 224 | 2 | 146 | 223 |
| 207 | S | NO | Route_A | Route_A | 3 | 31 | 188 | 103 | 19 |
| 242 | S | NO | Route_D | Route_D | 156 | 107 | 87 | 5 | 49 |
| 277 | N | NO | Route_A | Route_A | 1 | 23 | 231 | 16 | 5 |
| 279 | T | NO | Route_A,Route_D | Route_A | 2 | 15 | 235 | 6 | 1 |
| 280 | R | YES | Route_A | Route_A | 6 | 26 | 186 | 8 | 3 |

---

## 5. Full Hotspot Coverage (21 Positions)

| Position | Residue | A Rank | B Rank | C Rank | D Rank | In Shortlist | Recovery Routes | Best Route | V21-B Rank |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |
| 42 | S | 133 | 125 | 160 | 52 | NO | none | Route_D | 64 |
| 61 | S | 66 | 60 | 176 | 65 | NO | none | Route_B | 46 |
| 77 | T | 111 | 51 | 102 | 200 | NO | none | Route_B | 127 |
| 95 | K | 92 | 173 | 165 | 101 | NO | none | Route_A | 102 |
| 117 | L | 22 | 70 | 236 | 66 | NO | none | Route_A | 22 |
| 119 | Q | 32 | 165 | 182 | 199 | NO | none | Route_A | 86 |
| 140 | T | 101 | 1 | 193 | 121 | YES | Route_B | Route_B | 105 |
| 148 | K | 100 | 30 | 121 | 223 | NO | none | Route_B | 113 |
| 165 | G | 23 | 223 | 47 | 210 | NO | none | Route_A | 203 |
| 166 | S | 79 | 240 | 27 | 170 | NO | none | Route_C | 220 |
| 168 | I | 36 | 191 | 83 | 54 | NO | none | Route_A | 78 |
| 180 | A | 242 | 150 | 1 | 169 | YES | Route_C | Route_C | 242 |
| 186 | D | 9 | 34 | 80 | 105 | NO | none | Route_A | 26 |
| 187 | S | 8 | 9 | 240 | 87 | NO | none | Route_A | 4 |
| 188 | S | 28 | 5 | 239 | 55 | YES | Route_B | Route_B | 9 |
| 208 | I | 12 | 38 | 229 | 225 | NO | none | Route_A | 42 |
| 212 | N | 34 | 28 | 190 | 24 | NO | none | Route_D | 12 |
| 214 | S | 25 | 114 | 73 | 123 | NO | none | Route_A | 80 |
| 223 | S | 71 | 14 | 233 | 114 | NO | none | Route_B | 72 |
| 248 | A | 87 | 163 | 106 | 78 | NO | none | Route_D | 57 |
| 280 | R | 6 | 26 | 186 | 8 | YES | Route_A | Route_A | 3 |

---

## 6. Missed Hotspot Analysis

| Position | Best Route Rank | Best Route | Failure Class |
| :---: | :---: | :--- | :--- |
| 42 | 52 | Route_D | very_poor_all_routes |
| 61 | 60 | Route_B | very_poor_all_routes |
| 77 | 51 | Route_B | very_poor_all_routes |
| 95 | 92 | Route_A | very_poor_all_routes |
| 117 | 22 | Route_A | moderate_rank |
| 119 | 32 | Route_A | poor_rank |
| 148 | 30 | Route_B | poor_rank |
| 165 | 23 | Route_A | moderate_rank |
| 166 | 27 | Route_C | poor_rank |
| 168 | 36 | Route_A | poor_rank |
| 186 | 9 | Route_A | near_miss |
| 187 | 8 | Route_A | near_miss |
| 208 | 12 | Route_A | near_miss |
| 212 | 24 | Route_D | moderate_rank |
| 214 | 25 | Route_A | poor_rank |
| 223 | 14 | Route_B | moderate_rank |
| 248 | 78 | Route_D | very_poor_all_routes |

**Failure pattern summary**:
- moderate_rank: 4
- near_miss: 3
- poor_rank: 5
- very_poor_all_routes: 5

---

## 7. Proposed Atlas Output Format (Design Only)

```
═══════════════════════════════════════════════════
  HOTSPOT CANDIDATE — Position 280 (R)
═══════════════════════════════════════════════════
  Confidence:  HIGH (supported by 2 independent routes)

  Dominant Route:  SUBSTRATE / INTERFACE
    → Close to substrate binding surface (5.4 Å)
    → Accessible surface residue (RSA = 0.23)

  Secondary Route: FLEXIBILITY / DYNAMICS
    → High crystallographic flexibility (B-factor pctl = 0.96)
    → Located in loop region

  Evolutionary Context:
    → FVI = 5 (high family variability)
    → Observed in 6 different family consensus sets

  Top Substitution Proposals:
    1. R280A — family consensus (3 families), score 9
    2. R280E — family consensus (2 families), score 9
    3. R280K — family consensus (1 family), score 8

  ⚠ Evidence categories reflect structural and evolutionary
    context, not mechanistic proof of function.
═══════════════════════════════════════════════════
```

> [!NOTE]
> This format is for design review only. Not yet integrated into production.

---

## 8. Decision

**V21-B baseline**: 24 positions → 5/21 recovered (recall 0.238)
**V2.3 Multi-Route (Top6×4)**: 23 positions → 4/21 recovered (recall 0.190)

> [!NOTE]
> **RECOMMENDATION: KEEP V21-B.**
> Multi-route shortlist recovers 4/21 — does not exceed V21-B's 5/21.

---

## 9. Methodological Notes

- All route formulas were pre-specified and frozen BEFORE benchmark evaluation.
- No literature evidence (Known_mutations, Mutation_evidence) was used.
- No weights were optimized against the 21 development hotspots.
- Routes are kept INDEPENDENT — no global max or combined score.
- Primary shortlist: Top 6 per route, merged and deduplicated.
- All components normalized to 0–1 scales with equal-weight averaging within routes.