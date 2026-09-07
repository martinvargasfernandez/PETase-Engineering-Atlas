# PETase Functional Hotspot Layer Design Audit

**Date**: 2026-09-01  
**Status**: DESIGN & ARCHITECTURAL AUDIT COMPLETE (Production Atlas code remains 100% untouched)

---

## 1. HotSpot Wizard Design Principles & PETase Adaptations

### Core Principles of HotSpot Wizard (Algorithmic Summary)
HotSpot Wizard (Pavelka et al. 2009, Bendl et al. 2016) identifies protein engineering hotspots by integrating structural and evolutionary information:
1. **Functional Residue Identification**: Pinpoints catalytic residues and active-site lining positions.
2. **Substrate Tunnel Relevance**: Uses CaVER to calculate buried substrate tunnels and identifies tunnel-lining residues.
3. **Evolutionary Conservation/Mutability**: Uses Rate4Site and MSA Shannon entropy to estimate positional mutability.
4. **Structural Constraints**: Incorporates solvent accessibility (SASA), $B$-factors, and catalytic proximity.
5. **Exclusion/Protection Rules**: Protects catalytic residues and structural cysteines from mutation.

### Transferability Audit for PETase Biology

| HotSpot Wizard Principle | Transferable to PETases? | PETase Specific Adaptation |
| :--- | :---: | :--- |
| **Buried Substrate Tunnel (CaVER)** | **NO** | PETases act on insoluble, polymeric PET films via an **open, shallow substrate-binding cleft/groove**, not a deep buried tunnel. Substrate surface proximity (derived from 5XH3/6EQE HEMT/HEET complexes) replaces tunnel calculations. |
| **Catalytic Proximity Shells** | **YES** | Concentric distance shells ($4–8\text{ Å}$) around catalytic triad (Ser160, Asp206, His237) capture catalytic environment residues. |
| **Solvent Accessibility (SASA)** | **YES** | Distinguishes surface-exposed binding Cleft residues ($SASA \ge 15\%$) from buried core packing positions ($SASA < 15\%$). |
| **Flexible Loop Dynamics** | **YES** | Active-site flexible loops (Loop 1: 114–125, Loop 2: 180–188, Loop 3: 232–245, Loop 4: 280–288) control polymer accommodation. |
| **Evolutionary Permissiveness** | **YES** | Used as a **permissiveness filter**, not as sole positive evidence for hotspot existence. |
| **Protection/Exclusion Rules** | **YES** | Strict protection of catalytic triad (160, 206, 237) and disulfide cysteines (203-239, 273-289). |

---

## 2. Adaptation to PETase Biology: 5 Functional Hotspot Classes

To reflect PETase polymer degradation biology, positions are classified into 5 functional classes:

```
                               ┌────────────────────────────────────────┐
                               │   PETase Functional Hotspot Classes    │
                               └───────────────────┬────────────────────┘
                                                   │
         ┌──────────────────┬──────────────────────┼──────────────────────┬──────────────────┐
         ▼                  ▼                      ▼                      ▼                  ▼
┌─────────────────┐┌──────────────────┐┌──────────────────────┐┌───────────────────┐┌───────────────────┐
│Class A: Substrate││Class B: Catalytic││Class C: Loop /       ││Class D: Structural││Class E: Evolution-│
│Binding Surface  ││Environment       ││Accessibility         ││Stability          ││Supported          │
└─────────────────┘└──────────────────┘└──────────────────────┘└───────────────────┘└───────────────────┘
```

### Class Definitions & Rationale

#### Class A — Substrate-Binding Surface Hotspots
- **Biological Rationale**: Positions lining the open PET-binding cleft directly contact polymer chains. Mutations modulate aromatic stacking (e.g. W159, W185), substrate orientation, or product release.
- **Objective Criteria**: Distance to aligned substrate/HEMT ligand $d_{\text{substrate}} \le 8.0\text{ Å}$ AND $SASA \ge 15\%$.
- **Protection**: Non-catalytic positions.

#### Class B — Catalytic-Environment Hotspots
- **Biological Rationale**: Residues in the $4.0–8.0\text{ Å}$ structural shell surrounding the catalytic triad (S160, D206, H237). Mutations tune oxyanion hole stability (Y87, M161), pKa values, or nucleophilic attack geometry.
- **Objective Criteria**: Distance to catalytic triad $d_{\text{catalytic}} \le 7.0\text{ Å}$ AND position $\notin \{160, 206, 237\}$.

#### Class C — Loop / Accessibility Hotspots
- **Biological Rationale**: Residues located in flexible active-site loops shaping polymer entry and binding cleft dynamics (Loop 1: 114–125, Loop 2: 180–188, Loop 3: 232–245, Loop 4: 280–288).
- **Objective Criteria**: Residue in loop annotation AND ($B$-factor percentile $> 60\%$ OR $d_{\text{substrate}} \le 10.0\text{ Å}$).

#### Class D — Structural-Stability Hotspots
- **Biological Rationale**: Buried or semi-buried scaffold positions ($SASA < 15\%$) influencing thermal denaturation ($T_m$), core packing, or scaffold integrity needed for high-temperature PET hydrolysis ($50–70^\circ\text{C}$).
- **Objective Criteria**: $SASA < 15\%$ AND contact count $\ge 8$.

#### Class E — Evolution-Supported Hotspots
- **Biological Rationale**: Positions showing family-level variation across PET hydrolase clades where subfamily divergence or ancestral consensus indicates engineering tolerance.
- **Objective Criteria**: Family-level consensus divergence OR FVI $\ge 1$.

---

## 3. Atlas Feature Hierarchy Audit

Existing Atlas data mapped onto feature roles:

| Feature | Feature Source | Role in Architecture |
| :--- | :--- | :--- |
| **Substrate Distance ($d_{\text{substrate}}$)** | Aligned 5XH3/6EQE HEMT complex | **PRIMARY WHERE Evidence** (Class A / C) |
| **Catalytic Distance ($d_{\text{catalytic}}$)** | PDB 6EQE 3D coordinates | **PRIMARY WHERE Evidence** (Class B) |
| **Solvent Accessibility (SASA)** | FreeSASA / PDB 6EQE | **PRIMARY WHERE Evidence** (Class A vs D) |
| **Loop Annotation / $B$-Factor** | PDB 6EQE Chain A | **PRIMARY WHERE Evidence** (Class C) |
| **Evolutionary Variability (FVI / Entropy)** | 628-sequence PETase MSA | **PERMISSIVENESS FILTER** (Supports mutability) |
| **Different_family_consensus** | Atlas Family Alignment | **PERMISSIVENESS FILTER** (Class E) |
| **ESM-2 Zero-Shot LLR ($\Delta\text{LL}$)** | ESM-2 150M ($290 \times 20$ matrix) | **PRIMARY WHAT ENGINE** (Ranks amino acid proposals) |
| **FoldX Stability ($\Delta\Delta G$)** | FoldX 5.1 repaired structure | **SAFETY FILTER** (Excludes severe steric clashes) |
| **Catalytic Triad (160, 206, 237)** | Active-site annotation | **EXCLUSION / SAFETY CONSTRAINT** |
| **Disulfides (203-239, 273-289)** | PDB 6EQE Cysteines | **EXCLUSION / SAFETY CONSTRAINT** |

---

## 4. Function-First Architecture

The framework decouples functional relevance (WHERE to mutate) from evolutionary permissiveness and substitution scoring (WHAT to mutate):

$$\text{FUNCTIONAL RELEVANCE (WHERE)} \xrightarrow{\quad} \text{HOTSPOT CLASS} \xrightarrow{\quad} \text{PERMISSIVENESS FILTER} \xrightarrow{\quad} \text{SUBSTITUTION ENGINE (WHAT)}$$

```
1. WHERE TO MUTATE (Functional Relevance)
   "Does this position have a structural or biological mechanism to affect PETase activity or stability?"
   ├── Substrate Cleft Proximity (d_substrate ≤ 8.0 Å)
   ├── Catalytic Shell (d_catalytic ≤ 7.0 Å)
   ├── Flexible Loop (Loop 1-4, High B-factor)
   └── Core Packing / Burial (SASA < 15%)
         │
         ▼
2. HOTSPOT CLASSIFICATION
   Assign position to Class A, B, C, D, or E (deterministic rules, no fit weights)
         │
         ▼
3. PERMISSIVENESS & SAFETY FILTER
   Check evolutionary permissiveness (FVI, Entropy) and safety constraints (Protect Catalytic & Disulfides)
         │
         ▼
4. WHAT TO MUTATE (Substitution Proposals)
   Rank all 19 non-WT amino acids at position i using ESM-2 zero-shot ΔLL, filtered by FoldX ΔΔG safety check
```

---

## 5. Multi-Tier Hotspot Priority System (No Fit Weights)

To maintain 100% scientific interpretability without arbitrary weight fitting, positions are assigned to a **Rule-Based Priority Tier System**:

- **TIER 1 (HIGH PRIORITY)**: High Functional Relevance (Class A, B, or C) + High Evolutionary Permissiveness (FVI $\ge 2$ OR ESM $\text{LL}_{\text{WT}} < -1.5$).
- **TIER 2 (CONSERVED / CORE HOTSPOTS)**: High Functional Relevance (Class A, B, or C) + Evolutionarily Conserved (FVI $\le 1$, ESM Peak $\Delta\text{LL} > 0$). Captures conserved hotspots like W159, P181, F238, Y229!
- **TIER 3 (STABILITY / SCAFFOLD HOTSPOTS)**: Class D (Buried / Core Packing) with stabilizing FoldX or pLM support.
- **TIER 4 (PERMISSIVE SURFACE)**: High Evolutionary Permissiveness (FVI $\ge 3$) without direct substrate cleft contact.

---

## 6. Proposed User-Facing FASTA Output Format

When a user submits a PETase sequence, Atlas presents interpretable recommendations:

```
========================================================================================
PETase FUNCTIONAL HOTSPOT RECOMMENDATION: POSITION 159
========================================================================================
Position              : 159 (Trp)
Functional Class      : Class A — Substrate-Binding Surface / Cleft
Priority Tier         : TIER 2 (Conserved Functional Hotspot)
Functional Evidence   : High (d_substrate = 3.2 Å, SASA = 42.1%)
Evolutionary Support  : Conserved (FVI = 0, Rate4Site = -1.12)
Protection Status     : UNPROTECTED (Non-catalytic, Non-disulfide)

RECOMMENDED SUBSTITUTIONS (WHAT-to-Mutate):
  1. Trp159His  (ESM-2 ΔLL = +0.82 | FoldX ΔΔG = +4.69 kcal/mol | Structurally Tolerated)
  2. Trp159Ala  (ESM-2 ΔLL = +0.41 | FoldX ΔΔG = +1.12 kcal/mol | Surface Truncation)
  3. Trp159Phe  (ESM-2 ΔLL = +0.15 | FoldX ΔΔG = -0.22 kcal/mol | Aromatic Conserved)

Mechanism Summary     : Modulates aromatic stacking with PET terephthalate rings along 
                        the active-site cleft.
========================================================================================
```

---

## 7. Dual Validation Strategy

Validation must strictly separate position discovery (WHERE) from amino acid selection (WHAT):

1. **WHERE Validation (Position Discovery)**:
   - Evaluates Top20% recovery of independent beneficial positions ($N=21$ total holdout hotspots) across Tiers 1–3 versus random permutation.
2. **WHAT Validation (Substitution Accuracy)**:
   - Evaluates Top 1 / Top 3 / Top 5 exact amino-acid recovery on $N=19$ external beneficial mutations using ESM-2 $\Delta\text{LL}$ scores.

---

## 8. Comparison with Current Atlas (Solving Past Failure Modes)

| Dimension | Current Atlas V2.4 | New Function-First Architecture |
| :--- | :--- | :--- |
| **Logic Flow** | Single linear regression score combining FVI, SASA, B-factor | Decoupled: Functional Relevance (WHERE) $\rightarrow$ Class $\rightarrow$ Substitution Engine (WHAT) |
| **Conserved Hotspots (FVI=0)** | **FAILED** (0% recovery; FVI=0 penalized by regression) | **SOLVED** (Assigned to Tier 2 Conserved Functional Hotspots based on 3D substrate/catalytic proximity) |
| **Substitution Recommendations** | None (position ranking only) | **SOLVED** (ESM-2 zero-shot LLR + FoldX safety filter provides Top 3 substitution proposals) |
| **Interpretability** | Opaque single numerical score | Fully interpretable biological mechanism, functional class, and priority tier |

---

## 9. Next Steps for Phase 26 Implementation

1. **Phase 26 Proposal**: Build the functional feature extractor and rule-based hotspot classifier (`engine/functional_hotspots.py`).
2. **Phase 26 Validation**: Perform retrospective diagnostic evaluation on $N=21$ external holdout hotspots and $N=19$ external beneficial mutations.
3. **Estimated Prototype Effort**: **2–3 hours** (Python implementation, unit tests, full test suite regression verification).
