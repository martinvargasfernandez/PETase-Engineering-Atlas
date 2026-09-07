# Retrospective Blinded Validation Report: Evolutionary-Only Signal

**Date**: 2026-09-06
**Atlas Version**: 1.0
**Scoring Rules**: Pure evolutionary features only (FVI, Global Conservation, Family Consensus counts). Published mutation evidence masked.

---

## 1. Quality Control & Prediction Hash Verification
Before launching the analysis, the frozen predictions generated during Phase 2 were validated to ensure byte-level integrity.
* **frozen_position_ranking.tsv**:
  * Status: **VERIFIED**
  * Observed Hash: `962274848adfc82668b11c183eeef68ce784822731e2517cb3f0a8d6ebbaa286`
  * Expected Hash: `962274848adfc82668b11c183eeef68ce784822731e2517cb3f0a8d6ebbaa286`
* **frozen_mutation_ranking.tsv**:
  * Status: **VERIFIED**
  * Observed Hash: `d7d0fc6c9696ad86ad96a49066d7bc3b9f508d9a9d47287e3e622a78bbe351a0`
  * Expected Hash: `d7d0fc6c9696ad86ad96a49066d7bc3b9f508d9a9d47287e3e622a78bbe351a0`

---

## 2. Benchmark Audit & Evaluability

### Scopes and Limitations
The validation dataset is derived from peer-reviewed literature on PET hydrolase engineering. 
* **Combinatorial Limitation**: The current dataset contains exclusively single-substitution records. There are zero multi-mutant variants (e.g., FAST-PETase or DuraPETase combined constructs) included in these counts. All effects are attributed to single residue changes.
* **Engineered-Background Separation**: A subset of single mutations was tested on pre-engineered/thermostabilized scaffolds (TS-PETase, TSP-PETase, TSP-S238N-PETase). Because these mutations were not tested in isolation on wild-type backgrounds, their effects are context-dependent. They are strictly separated into the **Secondary/Contextual (Expanded)** benchmark, keeping the **Primary (Strict)** benchmark limited to wild-type or single-mutant backgrounds.

### Cohort Demographics
* **Strict Benchmark (Primary)**:
  * Total beneficial mutation records: `27`
  * Unique mapped beneficial positions: `25`
  * **Evaluable strict positions**: `21`
  * **Non-evaluable strict positions**: `4` (Exclusions due to FVI=0: position 159, 181, 229, 238)
* **Expanded Benchmark (Secondary)**:
  * Total beneficial mutation records: `31`
  * Unique mapped beneficial positions: `27`
  * **Evaluable expanded positions**: `22`
  * **Non-evaluable expanded positions**: `5` (Exclusions due to FVI=0: position 159, 181, 229, 238, 290)

---

## 3. Pre-Specified Primary Endpoint Analysis (Strict Benchmark)

### Cutoff Analysis
The primary pre-specified scientific endpoint is the **Recall of Strict Beneficial Positions within the Top 10%** of the 243 eligible positions (integer cutoff: **24 positions**, rounded down from 24.3 via floor-rounding).

* **Eligible Universe Size**: 243 positions
* **Selected Positions (Top 10% Cutoff)**: 24 positions
* **Recovered Strict Positions**: `1`
* **Total Evaluable Strict Positions**: `21`
* **Observed Recall**: `0.0476`
* **Random Expected Recovery**: `2.0728`
* **Fold Enrichment**: `0.4824`
* **Empirical One-Sided P-value** (1,000,000 permutations, seed=42): `0.897914`
* **Analytical Hypergeometric P-value** (Cross-check): `0.898176`

### Secondary Cutoff Analysis (Strict Benchmark)
* **Top 5% (N=12)**:
  * Recovered: `0`
  * Recall: `0.0000`
* **Top 20% (N=48)**:
  * Recovered: `3`
  * Recall: `0.1429`
* **Top 25% (N=60)**:
  * Recovered: `4`
  * Recall: `0.1905`

---

## 4. Rank-Based Distribution Analysis (Strict Benchmark)

To evaluate performance independent of arbitrary cutoffs, we checked the rank distribution of the `21` evaluable strict beneficial positions across the 243 eligible rankings.

* **Median Rank of Positives**: `106.0` / 243
* **Median Percentile Rank**: `56.79%`
* **Mann-Whitney U Test (One-sided rank-sum comparison)**:
  * U-statistic: `2291.0`
  * P-value: `0.448958`
  *(Note: A one-sided less-alternative Mann-Whitney U test checks if the rank distribution of positives is shifted toward lower/better values relative to non-positives).*

---

## 5. Secondary Exact-Substitution Analysis (Strict Benchmark)

We compared the literature-blind frozen mutation proposals against exact, individually validated beneficial substitutions.

* **Total Evaluable strict mutations**: `22`
* **Recovered exact substitutions**: `13`
* **Exact mutation recall**: `0.5909`

---

## 6. Expanded Benchmark Exploratory Analysis (Secondary)

This exploratory analysis repeats the position-level statistics using the expanded validation universe (which includes single mutations on engineered backgrounds).

* **Total Selected Positions (Top 10% Cutoff)**: 24 positions
* **Recovered Expanded Positions**: `1`
* **Total Evaluable Expanded Positions**: `22`
* **Observed Recall**: `0.0455`
* **Random Expected Recovery**: `2.1717`
* **Fold Enrichment**: `0.4605`
* **Empirical One-Sided P-value** (1,000,000 permutations, seed=42): `0.909077`
* **Analytical Hypergeometric P-value** (Cross-check): `0.909184`
* **Median Rank of Expanded Positives**: `107.0` / 243
* **Median Percentile Rank**: `56.38%`
* **Mann-Whitney U Test (One-sided)**:
  * U-statistic: `2404.0`
  * P-value: `0.466416`

---

## 7. Conclusions & Scientific Takeaways
The retrospective validation using purely evolutionary-only signals has been successfully executed under a strict blind. The primary Top 10% recall endpoint, empirical null models, and rank-based distributions have been permanently recorded.
