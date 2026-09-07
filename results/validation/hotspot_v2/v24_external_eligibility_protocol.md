# Hotspot V2.4 External Validation Eligibility Protocol

**Date**: 2026-08-31
**Status**: FROZEN (Before literature expansion search)

This protocol establishes strict, pre-specified eligibility rules for curating new beneficial PETase hotspot positions to form a prospective, independent external validation benchmark for the frozen Hotspot V2.4 model.

---

## 1. Primary External Benchmark Eligibility Rules (STRICT)

A candidate literature record **MUST** satisfy ALL of the following criteria to be included in the **PRIMARY** external validation benchmark:

1. **Target Enzyme Scope**: Must be a PET-degrading enzyme (e.g., *Ideonella sakaiensis* PETase, Leaf-branch Compost Cutinase (LCC), *Thermobifida fusca* cutinase, *Actinomadura* PETase, or engineered variants such as FAST-PETase, TurboPETase, HotPETase) capable of unambiguous pairwise alignment to the IsPETase reference sequence (PDB 6EQE Chain A).
2. **Explicit Substitution**: Must report an explicit single amino-acid substitution (e.g., S238N, R280A).
3. **Experimental Validation**: Must provide direct, quantitative experimental evidence of a beneficial phenotype (thermostability $\Delta T_m > 0.5^\circ\text{C}$, increased PET depolymerization rate, improved BHET/MHET hydrolysis, or enhanced binding affinity under PET-relevant conditions).
4. **Individual Evaluation**: The substitution must be evaluated as an individual single mutant (or individually de-convoluted within a combinatorial study). Substitutions inferred *only* from multi-mutant combinations without single-mutant data are excluded from Primary.
5. **Strict Independence**: Neither the position nor the publication may have been used during Hotspot V2 / V2.1 / V2.2 / V2.3 / V2.4 model development (specifically excluding the 21 development positions: `{42, 61, 77, 95, 117, 119, 140, 148, 165, 166, 168, 180, 186, 187, 188, 208, 212, 214, 223, 248, 280}`).

---

## 2. Secondary External Benchmark Category (EXPLORATORY)

Records failing one or more Primary criteria may be curated into the **SECONDARY** exploratory category:

- Substitutions inferred from multi-mutant engineering (e.g., FAST-PETase, HotPETase, DepoPETase) where individual single-mutant data are absent.
- Qualitative or single-concentration activity enhancements without full kinetic/thermal quantification.
- Non-standard assay conditions (e.g., soluble ester substrates like $p$-NPB without PET hydrolysis validation).

*Note: Secondary benchmark records will be analyzed separately and will NOT be mixed into the Primary independent validation score.*

---

## 3. Strict Exclusion Criteria

A literature record **MUST BE EXCLUDED** if:

- It overlaps with any of the 21 V2.4 development hotspot positions.
- It is purely computational (e.g., MD simulation or Rosetta prediction without experimental synthesis and testing).
- It represents a neutral, silent, or deleterious mutation.
- Coordinate mapping to the IsPETase reference sequence is ambiguous or unresolvable.
