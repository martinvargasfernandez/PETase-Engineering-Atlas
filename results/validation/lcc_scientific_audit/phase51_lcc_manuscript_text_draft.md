# Manuscript-Ready Text Drafts: LCC Case Study (Phase 51)

## 1. Methods: Query-Sequence Coordinate Mapping
```text
Query sequences submitted to the PETase Engineering Atlas are mapped onto the master IsPETase_v1 reference coordinate system using global Dynamic Programming pairwise alignment (Biopython PairwiseAligner implementation with BLOSUM62 substitution matrix and affine gap penalties). Mapping operates strictly at the individual residue level, assigning each query amino acid position to its corresponding homologous reference position based on alignment column indices. This sequence-driven mapping eliminates the need for manual signal-peptide truncation or fixed positional offsets, ensuring robust reference-coordinate assignment across homologs with variable N-terminal leader lengths, sequence extensions, or internal insertions/deletions.
```

## 2. Results: LCC Case-Study Validation
```text
To evaluate Atlas performance on a distant thermophilic homolog, we analyzed the wild-type sequence of Leaf-branch compost cutinase (LCC; 259 mature amino acids, 51.6% alignment identity to IsPETase). Without requiring a 3D query structure, the Function-First prioritization engine generated a shortlist of 30 candidate engineering positions. This shortlist successfully captured major active-site engineering hotspots previously identified in literature, including positions corresponding to LCC Y93 (Rank #5), H218 (Rank #8), and F243 (Rank #3). 

Furthermore, evolutionary WHAT substitution ranking—derived from amino-acid frequencies across the 628-sequence PETase master alignment—recovered exact beneficial literature mutations. Specifically, LCC H184Y (literature H218Y [Cribari et al. 2023, Orr et al. 2024]) was identified as the #1 evolutionary proposal at reference position 214 (115 MSA sequences), while LCC F209I (literature F243I [Cui et al. 2021]) was prioritized among the top evolutionary substitutions at reference position 238.
```

## 3. Discussion: Transferability & Limitations of Reference Structural Annotations
```text
A central feature of the Engineering Atlas is the projection of reference structural context (substrate proximity, catalytic distance, and relative surface accessibility calculated on IsPETase PDB 6EQE) onto mapped query sequences. Direct comparison against the experimental 1.50 Å crystal structure of wild-type LCC (PDB 4EB0) confirmed that reference-transferred annotations reliably distinguish exposed active-site cleft residues from buried core positions. However, quantitative comparison revealed localized distance variations resulting from backbone loop shifts between IsPETase and LCC active sites (e.g., catalytic distance for LCC A179 / Ref 209 measured 5.08 Å in 6EQE versus 11.23 Å in 4EB0). 

These findings emphasize that reference structural annotations function as informative coordinate-level context for hypothesis generation rather than exact, query-specific 3D measurements. By maintaining an explicit separation between sequence-derived evolutionary evidence and reference structural context, the Atlas provides transparent, robust prioritization across diverse PET-degrading enzymes.
```

## 4. Limitations: Reference-Context vs Query-Specific Structural Evidence
```text
While the PETase Engineering Atlas effectively prioritizes functional engineering positions across diverse homologs, several scientific limitations should be noted. First, structural descriptors presented in the workspace (such as substrate distance and SASA) represent projected annotations from the IsPETase 6EQE crystal structure and do not reflect query-specific 3D atomic coordinates or dynamic conformational states. Second, evolutionary WHAT proposals reflect global consensus frequencies across the broader PETase family rather than clade-restricted sub-family distributions. Finally, inclusion in the Function-First Top30 shortlist signifies high structural and evolutionary priority for engineering exploration rather than a deterministic guarantee of increased depolymerization activity.
```
