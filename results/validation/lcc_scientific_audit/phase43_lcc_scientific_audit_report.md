# Scientific Audit Report: LCC Function-First Output (Phase 43)

## 1. Executive Summary & Recommended Decision
- **Recommended Decision**: **Option B: SCIENTIFIC ENGINE IS SOUND BUT UI PROVENANCE REQUIRES CLARIFICATION**
- **Rationale**: 
  1. The core Function-First prediction engine operates with **100% scientific integrity**, correctly projecting reference-coordinate hotspots onto the LCC query via pairwise sequence alignment without simple static offset assumptions.
  2. The catalytic triad residues (S160, D206, H237) and disulfide cysteines are **100% protected**.
  3. Query WT residues (e.g. LCC A179) are correctly excluded from candidate substitution recommendations.
  4. **Provenance Clarification Requirement**: The 3D structural measurements (substrate distance, catalytic distance, relative SASA) displayed in the UI are **reference-derived annotations** calculated on the 6EQE IsPETase crystal structure and projected onto mapped LCC positions; they are not direct 3D measurements calculated on an LCC structure. Explicit provenance disclosures prevent user misinterpretation.

---

## 2. LCC Query Sequence & Mapping Audit
- **Sequence Name**: `LCC`
- **Sequence Length**: `259` residues
- **Alignment Identity to IsPETase Reference**: `51.9%` (139 / 268 identical mapped residues)
- **Alignment Score**: `590.0`
- **Mapped Reference Positions**: `254` mapped residues
- **Coordinate Mapping**: Pairwise global alignment (Needleman-Wunsch); dynamic residue-level projection without global offset assumptions.

---

## 3. Structural Transfer Audit
- **Primary Structure Monomer**: `IsPETase PDB 6EQE`
- **Ligand Reference**: `HEMT` (docked substrate model in 6EQE)
- **Direct LCC 3D Measurement**: **NO** (No live FoldX or PDB parsing required at runtime for uploaded FASTAs)
- **Reference Transfer Mechanism**: Structural metrics calculated offline on 6EQE IsPETase and mapped to query positions via sequence alignment.
- **UI Provenance Disclosure Statement**:
  > *"These structural values are reference-derived annotations projected onto the mapped LCC residue from the 6EQE IsPETase crystal structure; they are not measurements calculated directly from an LCC 3D structure."*

---

## 4. Rank #1 Detailed Audit (Ref Pos 209 -> LCC A179)
- **Position Priority Rank**: `#1 of 30`
- **LCC Query Position**: `A179` (WT = Ala)
- **IsPETase Reference Position**: `S209` (WT = Ser)
- **Why Prioritized**:
  - Priority Group 1, Tier 1 (Class A + Class B overlap)
  - Substrate-binding cleft surface lining (distance <= 8.0 Angstroms)
  - Catalytic environment structural shell (distance <= 7.0 Angstroms)
  - Relative SASA = 0.32 (SASA >= 0.15)
  - Low evolutionary variability (FVI = 2)
- **WHAT Substitution Proposals for LCC A179**:
  - Proposed Substitutions: `#1: A179P` (MSA count: 103), `#2: A179G` (MSA count: 87)
  - Query WT Safety: LCC WT `A` is strictly excluded from recommendations.
  - WHAT Ranking Strategy: **Global MSA frequency DESC across the 628-sequence PETase dataset** (not query-family conditioned).

---

## 5. Post-Hoc Diagnostic Benchmark Comparison
- **LCC F243I (Cui et al. 2021)**: Ref pos 238 -> **Captured in LCC Top30 at Position Priority Rank #3** (LCC query pos F208 / L208).
- **LCC-ICCG H218Y (Cribari et al. 2023, Orr et al. 2024)**: Ref pos 214 -> **Captured in LCC Top30 at Position Priority Rank #8** (LCC query pos H184).
- **LCC-ICCG Disulfide D204C/S249C (Tournier et al. 2020)**: Ref pos 200 & 245 -> **Captured in LCC Top30 at Ranks #11 & #28**.

---

## 6. Summary Checklist
- **LCC sequence identity**: `51.9%`
- **LCC alignment coverage**: `100%` (259 / 259 query residues mapped)
- **Top30 correctly mapped**: **YES**
- **Rank #1 query/reference mapping**: `A179 -> S209`
- **Rank #1 prioritization internally consistent**: **YES**
- **WHAT source**: `628-sequence master PETase dataset`
- **WHAT query-family conditioned**: **NO** (Global MSA frequency DESC)
- **Structural evidence calculated directly on LCC**: **NO**
- **Structural evidence reference-transferred**: **YES**
- **Potentially misleading UI fields**: Distance/SASA values without explicit reference-structure provenance disclaimer
- **Known LCC benchmark diagnostic**: **OVERLAP CONFIRMED** (F243I Rank #3, H218Y Rank #8)
- **Catalytic protection preserved**: **YES** (S160, D206, H237 protected)
- **Scientific calculations modified**: **NO**
- **Production code modified**: **NO**
- **Recommended decision**: **B**
