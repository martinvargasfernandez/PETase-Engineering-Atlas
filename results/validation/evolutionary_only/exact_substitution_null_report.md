# Retrospective Blinded Validation: Exact-Substitution Null Model Report

**Date**: 2026-09-06
**Observed Exact Recovery**: 13 / 22 (59.0909%)

---

## 1. Primary Null Model: Position-Conditional Proposal Null
The primary null model assumes that at each of the 22 evaluable positions, the Atlas draws one amino acid substitution uniformly at random from the actual frozen proposals available at that position in `frozen_mutation_ranking.tsv` (expected probability $p_i = 1 / n_i$ if present, else 0).

* **Expected Exact Recoveries**: 5.6670
* **Expected Recall**: 25.7593%
* **Fold Enrichment**: 2.2940
* **Empirical One-Sided P-value** (1,000,000 simulations, seed=42): 0.000001
* **Analytical Poisson-Binomial Expected Recoveries**: 5.6667
* **Analytical Poisson-Binomial P-value** (Cross-check): 0.000004

---

## 2. Secondary Null Model: Global Proposal-Frequency Null
The secondary sensitivity analysis constructs the overall amino-acid target frequency distribution across all proposals in `frozen_mutation_ranking.tsv`, and samples candidate substitutions stochastically at each position based on these global frequencies restricted to the allowable local proposal set.

* **Expected Exact Recoveries**: 5.0764
* **Expected Recall**: 23.0745%
* **Fold Enrichment**: 2.5609
* **Empirical One-Sided P-value** (1,000,000 simulations, seed=42): 0.000001

---

## 3. Locus-Level Statistical Independence Summary
An audit of the evolutionary alignment (`petase_atlas_v3_bacteria_taxonomy_clean_mafft.fasta` containing 628 sequences) verified that the MSA contains exclusively natural sequences. No engineered variants or literature point-mutant sequences were present, ensuring 100% independence of the exact-substitution validation.
