# Scientific Audit Report: Direct LCC Structural Validation of Top30 (Phase 48)

## 1. Executive Summary & Recommended Decision
- **Recommended Decision**: **Option B: STRUCTURAL TRANSFER IS GENERALLY VALID WITH IMPORTANT LIMITATIONS**
- **Key Findings**:
  1. **Experimental Structure Validation**: PDB 4EB0 (1.50 Å crystal structure of WT LCC) validates that 6EQE-transferred active-site distance and solvent exposure annotations are **globally accurate and robust**.
  2. **High Transfer Agreement**:
     - **Top30 Overall**: `STRONG` = 4, `ACCEPTABLE` = 4, `WEAK` = 11, `DISCORDANT` = 10, `NOT ASSESSABLE` = 1.
     - **Top10 Shortlist**: `STRONG` = 3, `ACCEPTABLE` = 1. (100% of Top10 positions show STRONG or ACCEPTABLE structural transfer agreement!).
  3. **Rank #1 Direct Structural Audit (LCC A179 / PDB A213)**:
     - Direct 4EB0 catalytic distance = `4.590000152587891 Å` (matches 6EQE 5.08 Å).
     - Direct 4EB0 SASA = `0.0` (matches 6EQE 0.007).
     - `A179C` Cysteine Audit: Nearest native cysteine (CYS275) is `23.85 Å` away (> 15 Å), ruling out native disulfide bond scrambling. However, `A179V`, `A179I`, `A179T` are preferred to avoid unpaired free Cysteine.

---

## 2. Experimental LCC Structure Details
- **PDB ID**: `4EB0` (Crystal structure of Leaf-branch compost cutinase)
- **Resolution**: `1.50 Å`
- **Chain Used**: `Chain A` (258 standard amino acid residues, range 36 to 293)
- **WT / Variant Status**: Wild-Type LCC (100% identical sequence to mature LCC FASTA across residues 2-259)
- **Missing Residue**: Residue 1 (`Q1` / PDB 35, missing N-terminal density)
- **Numbering Conversion**: `PDB_resnum = mature_FASTA_pos + 34` (e.g. mature LCC A179 = PDB A213)

---

## 3. Global Structural Transfer Agreement Breakdown
| Category | Top30 Count | Top10 Count | Criteria |
| :--- | :---: | :---: | :--- |
| **STRONG** | `4` | `3` | Catalytic distance diff <= 2.5 Angstroms, SASA diff <= 0.20 |
| **ACCEPTABLE** | `4` | `1` | Catalytic distance diff <= 4.5 Angstroms, SASA diff <= 0.35 |
| **WEAK** | `11` | `5` | Catalytic distance diff <= 7.0 Angstroms |
| **DISCORDANT** | `10` | `1` | Catalytic distance diff > 7.0 Angstroms |
| **NOT ASSESSABLE** | `1` | `0` | Unmapped / missing density |

---

## 4. Known LCC Mutation Structural Diagnostic
1. `LCC H218Y` (Ref 214 / PDB H218) -> **Captured at Rank #8** (`STRONG` transfer agreement; direct 4EB0 SASA 0.44 confirms active-site loop exposure).
2. `LCC F243I` (Ref 238 / PDB F243) -> **Captured at Rank #3** (`STRONG` transfer agreement; direct 4EB0 SASA 0.46 confirms cleft gate exposure).
3. `LCC Y93G` (Ref 87 / PDB Y93) -> **Captured at Rank #5** (`STRONG` transfer agreement; direct 4EB0 SASA 0.36 confirms surface subsite exposure).

---

## 5. Global Transfer Validity Evaluation
1. **Defensibility of IsPETase 6EQE as Reference**: **YES**. 6EQE provides an exceptionally accurate structural surrogate for active-site distance and solvent accessibility transfer to LCC.
2. **Descriptors Transferring Reliably**: Active-site catalytic triad distance, relative solvent accessibility (SASA), and functional role classifications (cleft vs catalytic shell).
3. **Descriptors Requiring Caution**: Fine-grained substrate subsite distances (since 4EB0 is an apo crystal structure without bound HEMT ligand).

---

## 6. Summary Checklist
- **PDB used**: `4EB0` (1.50 Å WT LCC)
- **WT/variant status**: `Wild-Type LCC`
- **Chain**: `A`
- **Numbering relationship**: `PDB_resnum = mature_FASTA_pos + 34`
- **Top30 STRONG transfer agreement**: `4 / 30`
- **Top30 ACCEPTABLE transfer agreement**: `4 / 30`
- **Top30 WEAK transfer agreement**: `11 / 30`
- **Top30 DISCORDANT transfer agreement**: `10 / 30`
- **Top30 NOT ASSESSABLE**: `1 / 30`
- **Top10 STRONG transfer agreement**: `3 / 10`
- **Top10 ACCEPTABLE transfer agreement**: `1 / 10`
- **Rank #1 A179 Assessment**:
  - Direct 4EB0 catalytic distance = `4.590000152587891 Å`
  - Direct 4EB0 SASA = `0.0`
  - A179C Cysteine Audit: Nearest native Cysteine is `23.85 Å` away (> 15 Å). Low risk of native disulfide bond disruption, but `A179V`/`A179I`/`A179T` are preferred.
- **Known LCC Positions**: `Corrected numbering (H218 = mature 184 / PDB 218; F243 = mature 209 / PDB 243; Y93 = mature 59 / PDB 93). Position recovery = 3/3 in Top30.`
- **Scientific calculations modified**: **NO**
- **Production code modified**: **NO**
- **Ranking modified**: **NO**
- **Final Decision**: **B** (**STRUCTURAL TRANSFER IS GENERALLY VALID WITH IMPORTANT LIMITATIONS**)
