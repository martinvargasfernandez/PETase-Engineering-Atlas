# PETase Engineering Atlas v3 — Manuscript Figure Data Package Provenance

This directory contains the reproducible, manuscript-ready data package extracted directly from the frozen PETase Engineering Atlas v3 and its scientific validation benchmarks (Blocks A and B).

## Scientific Caveats & Guidelines

When presenting or analyzing these datasets in the manuscript, the following frozen scientific findings must be strictly adhered to:
1. **Raw Proposal vs. End-to-End Recovery**: Raw proposal recovery (45.5% / 5-of-11 targets recovered) and user-facing end-to-end recommendation recovery (27.3% / 3-of-11 targets recovered) are distinct. The drop is due to position filtering.
2. **Lack of Position-Level Enrichment**: No statistically significant enrichment of beneficial mutations in the Top 10% or Top 5% position-ranking candidate pool was observed (observed enrichment is 0.0x, p = 1.0).
3. **FVI Limitations**: The Family Variability Index (FVI) is not a universal predictor of beneficial mutability. Rather, it reflects evolutionary consensus divergence.
4. **Small-Family Consensus Reliability**: The reliability of consensus assignments in small families (e.g., LCC-like with N=8, IsPETase-like with N=10) varies significantly under single-sequence dropouts.
5. **Position 159 FVI Stability**: Position 159 has a robust FVI = 0 across all Block B robustness analyses (100% stable).
6. **Position 229 Composition Sensitivity**: Position 229 is highly sensitive to sequence composition and resides near the FVI = 0/1 boundary (exhibiting eligibility shifts in 71.4% of jackknife/subsampling runs). It must not be labeled simply as "stable FVI=0".
7. **Evolutionary Plausibility vs. Fitness**: A mutation being evolutionary plausible (e.g., matching a family consensus state) does not guarantee improved fitness or activity.
8. **Independence of Validation**: Validation evidence already loaded into the Atlas model (e.g., FAST-PETase direct input residues) is not independent validation, which is why Sets A and B are strictly separated.

---

## File Provenance Summary

### 1. `figure1_metadata.tsv`
- **Purpose**: Provides verified metadata counts for Figure 1 labels.
- **Source Artifacts**: 
  - `atlas_v3/families/family_consensus_summary.tsv`
  - `atlas_v3/families/family_definitions.tsv`
  - `atlas_v3/atlas_v3_IsPETase_reference_table.tsv`
  - `validation/literature_benchmark/PETase_Validation_Dataset_v1_mapped.tsv`
  - `results/validation/literature_benchmark/benchmark4_per_mutation_results.tsv`
- **Extraction Method**: Simple aggregation and counting of records in the raw files.
- **Values Type**: Simple formatting/counting.
- **Known Limitations**: Total literature benchmark records (107) include non-single substitutions and out-of-scope mutations, whereas evaluable records (63) and primary substitutions (60) are restricted to single-substitution benchmarking scope.

### 2. `figure2_family_composition.tsv`
- **Purpose**: Contains the family counts and dataset fractions for Figure 2 composition analysis.
- **Source Artifacts**: `atlas_v3/families/family_consensus_summary.tsv`
- **Extraction Method**: Loads family sequence counts and divides by the total canonical sequence count (628).
- **Values Type**: Direct frozen values and simple fraction calculations.
- **Known Limitations**: Sequence counts represent the curated MSA representation, which is subject to taxonomic concentration.

### 3. `figure2_position_landscape.tsv`
- **Purpose**: Maps all 290 reference positions to their global/family consensus, global/family conservation, FVI, different consensus count, known mutation count, and catalytic triad protected status.
- **Source Artifacts**:
  - `atlas_v3/families/global_family_consensus_matrix.tsv`
  - `atlas_v3/families/family_variability_index.tsv`
  - `atlas_v3/known_mutations_atlas_v3.tsv`
- **Extraction Method**: Merges the global consensus matrix and family variability index on `IsPETase_position`, maps known mutation counts from `known_mutations_atlas_v3.tsv`, and flags positions S160, D206, and H237 as protected.
- **Values Type**: Direct frozen values joined together.
- **Known Limitations**: Conservation percentages are dependent on alignment gap handling and representation in the MSA.

### 4. `figure2_fvi_distribution.tsv`
- **Purpose**: Represents the frequency distribution of FVI values across the 290 reference positions.
- **Source Artifacts**: `atlas_v3/families/family_variability_index.tsv`
- **Extraction Method**: Counts the number of positions matching each FVI value and divides by 290.
- **Values Type**: Simple counting.
- **Known Limitations**: Constrained to the 290 mature IsPETase reference positions.

### 5. `figure3_robustness.tsv`
- **Purpose**: Provides robustness statistics under various subsampling and exclusion analyses.
- **Source Artifacts**: `results/validation/literature_benchmark/block_b_evolutionary_robustness.json`
- **Extraction Method**: Flattens nested JSON blocks for redundancy, random, and stratified subsampling, small-family jackknifing, Other_bacterial exclusion, and genus balancing into a long-format table.
- **Values Type**: Formatting of frozen summaries (replicates are consolidated into medians and 5th/95th percentiles in source).
- **Known Limitations**: Raw replicate-level data were not saved individually in the frozen JSON artifact; only the consolidated summaries (median, p5, p95) are available.

### 6. `figure3_key_positions.tsv`
- **Purpose**: Audits the evolutionary stability of FVI and candidate eligibility for key positions and catalytic positions.
- **Source Artifacts**: `results/validation/literature_benchmark/block_b_evolutionary_robustness.json`
- **Extraction Method**: Extracts FVI min/max, stability percentage, and subsampling eligibility percentages for target positions.
- **Values Type**: Direct frozen values.
- **Known Limitations**: Represents eligibility behavior under specific perturbation thresholds rather than physical thermodynamics.

### 7. `figure4_independent_mutations.tsv`
- **Purpose**: Detailed substitution-level results for the 11 independent beneficial validation mutations.
- **Source Artifacts**: `results/validation/literature_benchmark/benchmark4_per_mutation_results.tsv`
- **Extraction Method**: Filters for Set A Positive rows and outputs relevant mapping, rank, score, and eligibility values.
- **Values Type**: Direct frozen values.
- **Known Limitations**: Restricted to the independent beneficial subset (Set A Positive) to prevent circularity from directly-informed or position-informed mutations.

### 8. `figure4_statistics.tsv`
- **Purpose**: Consolidates statistical significance tests (Poisson binomial and Monte Carlo simulation observed/expected rates and p-values) for validation recovery.
- **Source Artifacts**:
  - `results/validation/literature_benchmark/benchmark5_summary.json`
  - `results/validation/literature_benchmark/block_a_statistical_robustness.json`
- **Extraction Method**: Loads and formats statistical fields.
- **Values Type**: Direct frozen values.
- **Known Limitations**: Uniform Amino Acid Null model assumes equal likelihood of all 19 non-WT residues, whereas empirical null models account for observed substitution frequencies.

### 9. `figure5_case_studies.tsv`
- **Purpose**: Detailed data for biological case studies (positions 140, 159, 205, 229).
- **Source Artifacts**: `results/validation/literature_benchmark/benchmark4_per_mutation_results.tsv`
- **Extraction Method**: Filters for the 4 case study positions, maps FVI range from Block B audit, and appends family consensus states.
- **Values Type**: Direct frozen values.
- **Known Limitations**: Summarizes validation performance metrics but does not infer structural or enzymatic mechanisms.

### 10. `figure5_family_states.tsv`
- **Purpose**: Family-resolved consensus states and conservation scores for the 4 case study positions to permit heatmap plotting.
- **Source Artifacts**: `atlas_v3/families/global_family_consensus_matrix.tsv`
- **Extraction Method**: Queries the consensus and conservation values for each of the 9 families at positions 140, 159, 205, and 229, checking matching flags against IsPETase WT and experimental beneficial mutants.
- **Values Type**: Direct frozen consensus states combined with boolean matching.
- **Known Limitations**: Restricted to mature reference coordinates.
