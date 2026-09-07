# Conceptual Validation Figure Plan: PETase Engineering Atlas (Phase 52)

*This document outlines the conceptual structure of the primary multi-panel validation figure for the manuscript.*

---

## Main Manuscript Figure: Methodological Overview & Formal Validation
- **Panel A: Overview of the Function-First Atlas Workflow**
  - Conceptual schematic showing query FASTA sequence input $ightarrow$ reference alignment mapping $ightarrow$ Function-First WHERE filtering (catalytic/cleft proximity + evolutionary variability) $ightarrow$ Evolutionary WHAT substitution ranking $ightarrow$ interpretable engineering shortlist.
- **Panel B: Search-Space Reduction & WHERE Positional Enrichment**
  - Bar chart comparing observed WHERE Top30 positional recovery ($5/15 = 33.3\%$) against uniform random expectation ($1.71/15 = 11.4\%$), highlighting **2.92-fold enrichment ($p = 0.01798$)** and **89.7% search-space reduction** (30/290 positions).
- **Panel C: Evolutionary WHAT Substitution Recovery**
  - Stacked bar chart decomposing Evolutionary WHAT performance on captured positions: Top1 ($2/5$), Top3 ($2/5$), Top5 ($4/5 = 80\%$), demonstrating high conditional substitution accuracy.
- **Panel D: End-to-End Workflow Performance**
  - Performance breakdown showing end-to-end recovery across the complete literature-blind benchmark ($N=15$).
- **Panel E: LCC Supporting Case Study**
  - Structural view of LCC (PDB 4EB0) showing Function-First Top30 mapped positions and recovery of literature benchmark sites (H218, F243, Y93).

---

## Supplementary Figures
- **Supplementary Figure 1: Layer 1 Evolutionary Substitution Signal Enrichment**
  - Detailed enrichment breakdown across 628-sequence alignment vs composition-aware null models ($3.83	imes$ enrichment, $p < 0.001$).
- **Supplementary Figure 2: Mapping & Coordinate Robustness Stress Tests**
  - Demonstration of reference-coordinate invariance across N-terminal extensions (+20, +34 aa) and indels (20/20 checks passed).
- **Supplementary Figure 3: Direct 4EB0 Structural Validation & Reference Transfer Comparison**
  - Direct comparison of 6EQE-transferred vs 4EB0-calculated catalytic distances and SASA values, illustrating active-site loop variations and explicit provenance disclosures.
