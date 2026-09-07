# Phase 20 — Low-Variability Energetic Feature Audit Report

**Date**: 2026-08-31
**Status**: AUDIT COMPLETE (No software installed, no models trained)

---

## 1. Task 1 — Software & Environment Availability

A comprehensive audit of the local environment and repository dependencies was conducted:

| Tool / Package | Status | Version / Path | Suitability for Biophysical Stability |
| :--- | :---: | :--- | :--- |
| **FoldX** | **NOT INSTALLED** | Not found in PATH | Primary choice for fast, empirical $\Delta\Delta G$ calculations |
| **Rosetta / PyRosetta** | **NOT INSTALLED** | Not found in PATH | High-accuracy structural modeling & flex-ddG |
| **OpenMM** | **NOT INSTALLED** | Not installed in Python env | GPU-accelerated molecular dynamics simulations |
| **ESM / PyTorch (pLM)** | **NOT INSTALLED** | `torch` / `esm` not installed | Zero-shot sequence-based mutational effect prediction |
| **SciPy / NumPy / Pandas**| **INSTALLED** | `scipy` v1.18.1 | Numerical processing & statistical analysis |
| **BioPython** | **INSTALLED** | `Bio` module available | PDB parsing & pairwise sequence alignments |

---

## 2. Task 2 — Existing Structural Input (PDB 6EQE Chain A)

The reference crystal structure of *Ideonella sakaiensis* PETase (PDB 6EQE Chain A) was audited for suitability in biophysical energy calculations:

- **Resolution & Quality**: Ultra-high resolution (**0.92 Å**), $R_{\text{free}} = 0.110$. Exceptional coordinate precision.
- **Residue Coverage**:
  - Missing residues: N-terminal signal peptide (res 1–28) and C-terminal His-tag (res 294–298) were not located in crystallography (REMARK 465).
  - Resolved region: **Residues 29 to 290** (all 262 mature enzyme positions are 100% resolved).
- **Disulfide Bonds**: Cys203–Cys239 and Cys273–Cys289 are intact and properly formed.
- **Catalytic Triad**: Ser160, Asp206, and His237 are 100% resolved with unambiguous electron density.
- **Heteroatoms & Buffer**: Contains crystallographic waters (`HOH`) and HEPES buffer molecules. Must be stripped prior to FoldX / Rosetta calculations.
- **Alternate Conformations**: High resolution yields split side-chain conformations (altloc A/B) for several surface residues. Standardization to single rotamer conformation is required.
- **Required Structural Repair**: Standard `FoldX --command=RepairPDB` or `Rosetta relax` is required to minimize minor background clashes before introducing point mutations.

---

## 3. Task 3 — Definition of Biophysical Energetic Features

To complement static geometric features (SASA, burial, active-site distance), the following biophysical energetic descriptors are pre-specified:

1. **$\Delta\Delta G_{\text{total}}$**: Predicted change in free energy of unfolding ($\Delta G_{\text{mut}} - \Delta G_{\text{wt}}$ in kcal/mol). Negative values indicate stabilizing mutations; positive values indicate destabilizing mutations.
2. **van der Waals Clash Penalty ($\Delta\text{VdW}$)**: Steric overlap energy resulting from bulky side-chain substitutions in tightly packed cores.
3. **Electrostatic Contribution ($\Delta E_{\text{elec}}$)**: Coulombic interactions, salt bridges, and surface charge alterations.
4. **Solvation & Hydrophobic Burial ($\Delta G_{\text{solv}}$)**: Desolvation penalty of polar groups vs. hydrophobic effect of burying non-polar side chains.
5. **Hydrogen-Bond Network Energy ($\Delta E_{\text{hbond}}$)**: Loss or creation of intra-molecular H-bonds.
6. **Side-Chain Rotamer Entropy ($\Delta S_{\text{rot}}$)**: Loss of conformational entropy upon burying flexible side chains.

### Feasibility Classification

- **Category A (Feasible Today)**: Static geometric & packing proxies already present in Atlas (`relative_SASA`, `residue_depth`, `packing_density`, `normalized_B_factor`).
- **Category B (Feasible with Software Installation)**: FoldX $\Delta\Delta G$ or ESM-1v zero-shot log-likelihood ratios.
- **Category C (Computationally Expensive)**: Rosetta flex-ddG or OpenMM alchemical Free Energy Perturbation (FEP).

---

## 4. Task 4 — Mutation-Level vs. Position-Level Integration

A fundamental distinction exists between **position-level** hotspot detection (WHERE to mutate) and **mutation-specific** energetic evaluation (WHAT to mutate):

```
FASTA Sequence
   │
   ▼
1. Sequence Alignment & Mapping (Atlas Reference Coordinates)
   │
   ▼
2. Hotspot Prioritization (WHERE to mutate)
   ├── Variable Route (V2.4): Evolutionary + SASA + B-factor (FVI ≥ 3)
   └── Conserved Route: Structural Centrality + Substrate Proximity + ΔΔG_min (FVI ≤ 2)
   │
   ▼
3. Evolutionary Mutation Proposal Engine (WHAT to mutate)
   │
   ▼
4. Energetic Stability Filter (FoldX / ESM-1v ΔΔG)
   ├── Reject destabilizing proposals (ΔΔG > +1.5 kcal/mol)
   └── Prioritize stabilizing / neutral proposals (ΔΔG ≤ +0.5 kcal/mol)
```

### Explicit Determination

- **Primary Role (Option B — WHAT to mutate)**: Energetic $\Delta\Delta G$ should serve primarily to **rank and filter candidate substitutions** proposed by the Atlas proposal engine, rejecting destabilizing mutations.
- **Secondary Role (Option A — WHERE to mutate)**: Energy connects to position-level hotspot detection by defining a position-level stability potential descriptor:
  $$\Delta\Delta G_{\text{min}}(i) = \min_{a \in \text{proposals}(i)} \Delta\Delta G(i \rightarrow a)$$
  which quantifies whether position $i$ accommodates stabilizing substitutions.

---

## 5. Task 5 — Architectural Recommendation for Phase 21

Four candidate computational approaches for capturing low-variability (FVI $\le$ 2) hotspots were evaluated:

| Approach | Expected Benefit | Runtime per Mutation | Installation Complexity | Suitability for FASTA Workflow | Suitability for Conserved Core Hotspots |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FoldX $\Delta\Delta G$** | **HIGH** | ~5–10 seconds | Simple standalone executable | **EXCELLENT** (via 6EQE reference template) | **EXCELLENT** (captures core packing & cavity fill) |
| **ESM-1v / ESM-2 pLM** | **VERY HIGH** | ~0.1 seconds (GPU/CPU) | Moderate (`pip install esm torch`) | **EXCELLENT** (direct sequence input) | **EXCELLENT** (captures evolutionary/structural constraints) |
| **Rosetta flex-ddG** | High | ~1–2 CPU hours | Complex (academic license + compilation) | Poor (slow) | High |
| **OpenMM MD** | Moderate | ~10–50 GPU hours | Complex | Poor (computationally prohibitive) | Moderate |

---

## 6. Decision & Phase 21 Roadmap

> [!IMPORTANT]
> **RECOMMENDED PHASE 21 ROUTE**: **FoldX $\Delta\Delta G$ or ESM-1v pLM Integration**.

FoldX $\Delta\Delta G$ and ESM-1v pLM embeddings offer the fastest, most scientifically defensible approach for detecting and scoring evolutionarily conserved (FVI $\le$ 2) hotspots. FoldX directly calculates steric clash penalties and hydrophobic cavity filling in conserved cores, while ESM-1v provides zero-shot mutational effect prediction directly from FASTA sequences.

### Phase 21 Implementation Plan (Summary)

1. Obtain and verify **FoldX 5.0** executable (or ESM-1v / ESM-2 model weights).
2. Run `RepairPDB` on PDB 6EQE Chain A to generate a clash-free reference structure.
3. Pre-compute FoldX $\Delta\Delta G$ for all 19 alternative amino acids across the 45 resolved FVI=0 reference positions.
4. Construct the position-level stability potential feature $\Delta\Delta G_{\text{min}}(i)$.
5. Evaluate whether adding $\Delta\Delta G_{\text{min}}(i)$ enables statistical discrimination ($p < 0.05$) for low-variability hotspots.
