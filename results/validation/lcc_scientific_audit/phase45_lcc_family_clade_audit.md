# Scientific Audit Report: LCC Family-Clade Classification (Phase 45)

## 1. Executive Summary
- **Classifier Module**: `engine.family_classifier.FamilyClassifier`
- **Classification Method**: Normalized, Shannon-entropy-weighted consensus agreement score across reference positions.
- **Exact LCC Classification Result**: `predicted_family = "ambiguous"` (`classification_status = "ambiguous"`, `confidence_status = "low"`)
- **Top 2 Candidate Families**:
  1. **Top Candidate**: `LCC-like` (Normalized Score: `0.4681`)
  2. **Runner-up Candidate**: `IsPETase-like` (Normalized Score: `0.4108`)
- **Score Margin**: `0.0573` (Threshold for unambiguous classification: `score_margin >= 0.0800`)
- **Bug Detected**: **NO** (The classifier functions strictly according to its mathematical formulation).
- **Classifier Modification Recommended**: **NO** (Preserves non-circular classification without forcing hardcoded identities).

---

## 2. Classification Algorithm & Decision Logic
The `FamilyClassifier` evaluates mapped study residues against consensus amino-acid profiles of 9 Atlas family clades:
1. **Shannon Entropy Weighting**: For each reference position $i$, weight $w_i$ is calculated based on consensus diversity across family clades. Positions where all family clades share the same consensus residue receive $w_i = 0.0$ (uninformative). Positions where consensus residues vary receive $w_i = -\sum p \log_2 p$.
2. **Normalized Agreement Score**: For each family clade $F$, score $S_F$ is calculated as the sum of weights $w_i$ for positions where the query residue matches family $F$'s consensus residue, normalized by the maximum possible score for family $F$:
   $$S_F = \frac{\sum_{i \in \text{mapped}} w_i \cdot \mathbb{I}(\text{query}_i == \text{consensus}_{F,i})}{\sum_{i \in \text{mapped}} w_i \cdot \mathbb{I}(\text{consensus}_{F,i} \text{ valid})}$$
3. **Threshold Rules**:
   - `mapped_positions < 50` or `max_score < 5.0` $\rightarrow$ `unclassified`
   - `best_score < 0.35` $\rightarrow$ `unclassified`
   - `score_margin (best_score - second_best_score) < 0.08` $\rightarrow$ `ambiguous`
   - Else $\rightarrow$ `classified` as `best_family`

---

## 3. LCC Classification Score Inventory
- **Sequence Analyzed**: LCC WT (259 aa, SHA256: `29c9d1952e82627f9ac27791b0d6cc1c97db753e07e9f1e152084732ca162f59`)
- **Normalized Consensus Scores across all 9 Atlas Family Clades**:
  - `LCC-like`: `0.4681`
  - `IsPETase-like`: `0.4108`
  - `Nocardiopsis-like`: `0.4047`
  - `Thermobifida-like`: `0.4028`
  - `Actinomadura-like`: `0.3915`
  - `Microbispora-like`: `0.3865`
  - `Other_bacterial`: `0.3468`
  - `Streptomyces-like`: `0.1667`
  - `Amycolatopsis-like`: `0.1088`

- **Decision Variable Evaluation**:
  - `best_score`: `0.4681` ($\ge 0.35$ threshold PASSED)
  - `second_best_score`: `0.4108`
  - `score_margin`: `0.0573` ($< 0.08$ threshold triggers `ambiguous` status)

---

## 4. Explanation for "ambiguous" Classification
1. **High Structural & Sequence Alignment Similiarity to Multiple Clades**: LCC is a thermophilic cutinase that shares high consensus agreement with both `LCC-like` and `IsPETase-like` across key active-site and structural positions.
2. **Narrow Score Margin**: Because LCC matches `LCC-like` at `46.8%` of informative positions and `IsPETase-like` at `41.1%` of informative positions, the margin (`0.0573`) falls below the strict 0.0800 confidence boundary.
3. **Biological Identity vs Clade Prediction**:
   - **Biological Identity**: Known LCC (Leaf-branch compost cutinase).
   - **Atlas Family-Clade Prediction**: Independently evaluated consensus agreement. The classifier correctly flags LCC as intermediate/ambiguous between closely related cutinase clades rather than making an overconfident incorrect assignment.

---

## 5. Scientific Summary Checklist
- **Classifier module**: `engine.family_classifier.FamilyClassifier`
- **Classification method**: Shannon-entropy-weighted normalized consensus agreement
- **Exact LCC result**: `predicted_family = "ambiguous"`
- **Relevant scores/thresholds**: Best (`0.4681`), Second (`0.4108`), Margin (`0.0573` < 0.0800)
- **Explanation for "ambiguous"**: Close consensus similarity between top candidate clades
- **Bug detected**: **NO**
- **Classifier modification recommended**: **NO** (Preserves objective classifier boundaries)
- **Top30 unchanged**: **YES**
- **WHAT unchanged**: **YES**
- **Mapping unchanged**: **YES**
- **Protection unchanged**: **YES**
- **Family classifier modified**: **NO**
- **Validation artifacts modified**: **NO**
