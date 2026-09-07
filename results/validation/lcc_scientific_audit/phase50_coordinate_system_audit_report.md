# Scientific Audit Report: Coordinate-System Integrity & LCC Numbering Audit (Phase 50)

## 1. Executive Summary & Final Decision
- **Final Decision**: **Option A: EXISTING COORDINATE SYSTEM IS ROBUST**
- **Justification**:
  1. **Residue-Level Dynamic Programming Alignment**: Production `ReferenceMapper` operates strictly via global Dynamic Programming pairwise alignment (`Biopython PairwiseAligner`). It maps individual residues based on alignment column indices, without using any fixed positional offsets or assuming signal-peptide lengths.
  2. **Stress Test Invariance**: Mapping stress tests demonstrate 100% reference-coordinate invariance across N-terminal extensions (+20 aa, +34 aa) and internal insertions/deletions. Homologous residues map to the exact same Atlas reference position regardless of query position shifts.
  3. **F208 / F209 Root Cause Resolved**: Production mapping for the literature `F243I` site is 100% correct: **Query Position = 209 (`F209`), Reference Position = 238 (`Ref F238`)**. The appearance of "F208" in Phase 47-49 text notes was an artifact of 0-based Python array indexing (`seq[208] == 'F'`).

---

## 2. Production Coordinate Mapping Architecture
- **Alignment Method**: Pairwise Global Alignment with affine gap penalties (`PairwiseAligner` using BLOSUM62 matrix).
- **Coordinate Assignment**:
  - `study_position = q_idx + 1` (1-indexed Query FASTA position).
  - `atlas_position = AtlasPosition(t_idx + 1)` (1-indexed IsPETase reference position).
- **Gaps & Indels**: Handled explicitly via `MappingStatus.INSERTION` (query insertion / reference gap) and `MappingStatus.DELETION` (query deletion / reference gap).
- **Fixed Offset Dependence**: **NONE**. No component assumes `query_pos + signal_peptide_len = ref_pos`.

---

## 3. Resolution of LCC F208 / F209 Inconsistency
- **Literature Mutation `F243I` (Cui et al. 2021)**: Published using full-length G9BY57 accession numbering (243).
- **Mature FASTA Position**: `243 - 34 = 209` (`F209` in mature LCC sequence).
- **Production Atlas Mapping**: **Query Position 209 (`F209`) $ightarrow$ Atlas Reference Position 238 (`Ref F238`)** with `EXACT_MATCH` status.
- **Root Cause of Inconsistency**:
  1. **0-based vs 1-based indexing**: Python array index `LCC_FASTA_SEQ[208]` evaluates to `'F'` (position 209), leading to transient notation of `F208` in scratch diagnostic text.
  2. **Separate Literature Mutation**: Tournier et al. (2020) published a completely separate mutation named `F209I` (full-length pos 209 $ightarrow$ mature pos 175 $ightarrow$ Ref 205, outside Top30).
- **Production Verification**:
  - **Is Production Query Position Correct?**: **YES** (`Query Pos 209`).
  - **Is Production Reference Position Correct?**: **YES** (`Atlas Ref Pos 238`).

---

## 4. Stress Test Results Summary
| Test Case | Tracked Site | Query Pos | Reference Pos | Alignment Invariance |
| :--- | :--- | :---: | :---: | :---: |
| Original Mature LCC | F209 (Ref 238) | 209 | 238 | **YES** |
| +20 N-terminal Extension | F209 (Ref 238) | 229 | 238 | **YES** |
| +34 N-terminal Extension | F209 (Ref 238) | 243 | 238 | **YES** |
| Internal +5 Insertion (pos 100) | F209 (Ref 238) | 214 | 238 | **YES** |
| Internal -5 Deletion (pos 100) | F209 (Ref 238) | 204 | 238 | **YES** |

---

## 5. Signal-Peptide Questions & Scientific Policy
1. **Does the Atlas NEED to know signal-peptide length to map an uploaded PETase sequence?**: **NO**. Alignment mapping is sequence-driven and automatically aligns homologous cutinase core regions regardless of N-terminal leader presence.
2. **Would different signal-peptide lengths across PETases invalidate the current coordinate system?**: **NO**. The residue-by-residue alignment handles variable leader lengths seamlessly.
3. **Would automatic signal-peptide prediction currently be necessary for Function-First prioritization?**: **NO**.

---

## 6. Summary Checklist
- **Mapping algorithm**: `Global Dynamic Programming Pairwise Alignment`
- **Residue-level or offset-based**: `Residue-level alignment`
- **Fixed signal-peptide assumption present**: **NO**
- **LCC Y93 mapping**: `Query Pos 59 (Y) -> Ref Pos 87 (Y)`
- **LCC H218 mapping**: `Query Pos 184 (H) -> Ref Pos 214 (S)`
- **LCC F243 mapping**: `Query Pos 209 (F) -> Ref Pos 238 (F)`
- **F208/F209 Root Cause**: `0-based array index notation (seq[208] == F) in scratch notes; production query pos is 209`
- **Production query coordinate correct**: **YES**
- **Production reference coordinate correct**: **YES**
- **Reference-coordinate invariance result**: **100% INVARIANT across all stress tests**
- **Signal peptides required for Atlas mapping**: **NO**
- **Variable signal-peptide lengths supported by current design**: **YES**
- **Scientific calculations modified**: **NO**
- **Production code modified**: **NO**
- **Mapping engine modified**: **NO**
- **Top30 modified**: **NO**
- **UI modified**: **NO**
- **Final Decision**: **A** (**EXISTING COORDINATE SYSTEM IS ROBUST**)
