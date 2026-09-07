# Hotspot V2.4 Literature Expansion Search Strategy & Targets

**Date**: 2026-08-31
**Status**: FROZEN (Targeting N >= 10 independent beneficial positions)

---

## 1. Gap Analysis & Benchmark Target

- **Current Independent Holdout Set**: **5 positions** (Positions 116, 159, 181, 229, 238).
- **Minimum Required Target**: **10 positions** (Need **5 additional** independent positions).
- **Desirable Target**: **15–20 positions** (Need **10–15 additional** independent positions).

---

## 2. Underrepresented Scaffolds & Literature Gaps

The 21 development positions were overwhelmingly dominated by **IsPETase** (Cui et al. 2021) and **DuraPETase** (Schreiber et al. 2024). The following major enzyme engineering efforts are **completely unrepresented or underrepresented** in the development set:

1. **FAST-PETase** (Lu et al. 2022, *Nature*): Engineered *Is*PETase variant containing N233K, R224Q, S121E, etc.
2. **HotPETase** (Bell et al. 2022, *Bioresources and Bioprocessing*): High-temperature engineered PETase.
3. **BahrTPETase / BahrPETase** (Pfaff et al. 2023 / Bahr et al. 2024): Novel bacterial PET hydrolase variants.
4. **LCC / LCC-ICCG / LCC-A2`** (Tournier et al. 2020, *Nature* / LCN studies): High-throughput mutagenesis of Leaf-branch Compost Cutinase.
5. **Thermobifida fusca Cutinase (TfCut2 / BTA hydrolase)** (Magalhães et al., Then et al.): Site-directed mutagenesis of thermophilic cutinases.
6. **BurtPETase / ThermoPETase** (Recent 2024–2025 structural and evolutionary engineering papers).

---

## 3. Recommended Structured Search Queries (PubMed / WoS / Scopus)

### Query Group 1: General PETase Mutation Engineering
```text
("PETase" OR "polyethylene terephthalate hydrolase" OR "PET hydrolase") 
AND ("site-directed mutagenesis" OR "directed evolution" OR "beneficial mutation" OR "thermostability" OR "activity enhancement")
AND NOT ("Cui" OR "Schreiber")
```

### Query Group 2: Scaffold-Specific Searches
- **FAST-PETase / HotPETase**:
  `("FAST-PETase" OR "HotPETase" OR "Lu et al." OR "Bell et al.") AND ("mutation" OR "variant")`
- **LCC Engineering**:
  `("Leaf-branch compost cutinase" OR "LCC-ICCG" OR "Tournier") AND ("mutant" OR "substitution" OR "thermostability")`
- **Thermobifida / Actinomycete Cutinases**:
  `("Thermobifida fusca" OR "TfCut2" OR "Est119") AND ("PET degradation" OR "mutation")`

---

## 4. Execution Workflow

1. Execute search queries across Literature databases.
2. Filter records against the **v24_external_eligibility_protocol.md**.
3. Map verified beneficial substitutions onto IsPETase reference coordinates.
4. Confirm $0$ overlap with the 21 V2.4 development positions.
5. Compile the expanded independent test set ($N \ge 10$) into `results/validation/hotspot_v2/v24_external_validation_dataset.tsv`.
6. Run frozen V2.4 model predictions and 10,000-iteration permutation test.
