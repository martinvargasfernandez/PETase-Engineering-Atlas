# Conserved Hotspot Benchmark Expansion Report (Phase 18)

**Date**: 2026-08-31

---

## 1. Executive Summary & Threshold Status

- **Primary Benchmark Target**: $\ge 12$ independent FVI=0 beneficial positions.
- **Current Total FVI=0 Independent Positions Available**: **6 / 12**
- **Total Low-Variability (FVI $\le$ 2) Independent Positions Available**: **14 / 15**
- **Benchmark Frozen Status**: **NO** (Target $N \ge 12$ not reached; $N = 6 < 12$).

> [!WARNING]
> Across all published PETase and cutinase engineering literature to date, only **6 independent reference positions** with $FVI = 0$ possess individually validated single beneficial mutations. The target threshold of $N \ge 12$ independent $FVI = 0$ positions cannot be met with currently available literature data.

---

## 2. Category Breakdown of Audited Low-Variability Mutations

### A. Category A — FVI=0 Primary Independent Benchmark Positions (N=6)

| Position | WT | Primary Mutation | Scaffold | Publication | Phenotype | DOI |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 159 | W | W159H | IsPETase | Meng et al. / Cui et al. | beneficial_activity | 10.1016/j.ijbiomac.2021.03.058 |
| 181 | P | P181A | IsPETase | Cui et al. | beneficial_thermostability | 10.1021/acscatal.0c05126 |
| 229 | F | F229Y | IsPETase | Meng et al. | beneficial_activity | 10.1016/j.ijbiomac.2021.03.058 |
| 238 | S | S238F | IsPETase | Cui et al. | beneficial_thermostability | 10.1021/acscatal.0c05126 |
| 102 | A | G62A | TfCut2 | Furukawa et al. | beneficial_activity | 10.1002/cbic.201800770 |
| 265 | D | F209S | TfCut2 | Furukawa et al. | beneficial_activity | 10.1002/cbic.201800770 |

### B. Category B — FVI=1–2 Primary Independent Benchmark Positions (N=8)

| Position | WT | Primary Mutation | Scaffold | Publication | FVI | Phenotype | DOI |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 116 | T | T116P | TS-PETase | Zhong-Johnson et al. | 2 | beneficial_thermostability | 10.1016/j.jbc.2024.105783 |
| 234 | G | A182V | TfCut2 | Mrigwani et al. | 1 | beneficial_thermostability | 10.1016/j.ijbiomac.2023.123512 |
| 241 | N | F243I | LCC | Tournier et al. | 1 | beneficial_activity | 10.1038/s41586-020-2149-4 |
| 282 | S | S283C | LCC | Tournier et al. | 1 | beneficial_disulfide | 10.1038/s41586-020-2149-4 |
| 133 | Q | L93F | PHL7 | Sonnendecker et al. | 1 | beneficial_activity | 10.1038/s41467-022-29892-9 |
| 281 | V | S226P | Cut190 | Oda et al. | 2 | beneficial_thermostability | 10.1016/j.jbb.2018.05.008 |
| 200 | I | R157A | HiC | Shirke et al. | 2 | beneficial_thermostability | 10.1021/acs.biochem.7b01149 |
| 260 | R | D204C | TfCut2 | Then et al. | 1 | beneficial_disulfide | 10.1002/bit.25583 |

---

## 3. Conclusions and Next Steps

1. **Hold Benchmark Freeze**: As $N = 6 < 12$ for FVI=0 positions, no new frozen benchmark file is created.
2. **Future Strategy**: Developing a robust conserved-route predictor will require prospectively testing candidate core/conserved structural positions in wet-lab assays or molecular dynamics simulations to expand the ground-truth dataset beyond $N=6$.