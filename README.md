# PETase Engineering Atlas

**A Group-Aware Evolutionary Framework for Prioritizing Mutation Hypotheses in PET Hydrolases**

PETase Engineering Atlas is a bioinformatic framework for prioritizing engineering positions and candidate amino-acid substitutions in PET hydrolases using evolutionary information integrated with reference-derived structural context.

This repository contains the software implementation, frozen Atlas resources, validation datasets and outputs, reproducibility scripts, tests, and figure-source data associated with the PETase Engineering Atlas study.

## Scope

The Atlas was constructed from **628 curated bacterial PET-hydrolase-related sequences** organized into nine operational sequence groups.

The framework separates mutation prioritization into two stages:

- **WHERE** - prioritization of candidate engineering positions.
- **WHAT** - ranking of candidate substitutions at selected positions.

The production WHERE workflow returns a fixed **Top30** shortlist.

Structural descriptors used by the framework are precomputed in the IsPETase reference context and transferred through homologous Atlas coordinates. They therefore represent **reference-derived structural context**, not query-specific three-dimensional measurements or structural predictions.

The Atlas is intended to prioritize experimentally testable engineering hypotheses and reduce the mutation search space. It does not directly predict the probability that an individual mutation will improve catalytic activity.

## Atlas coordinate system

The evolutionary Atlas is mapped to a common **290-position full-length IsPETase reference coordinate system**, including the native signal peptide.

Residue mapping for query sequences is performed using pairwise sequence alignment rather than fixed residue-number offsets, allowing the system to handle signal-peptide differences, substitutions, insertions, and deletions.

Protected catalytic positions include:

- S160
- D206
- H237

## Repository structure

```text
PETase_Engineering_Atlas_Publication/
├── atlas_v3/
├── data/
│   └── figure_data/
├── results/
│   └── validation/
├── scripts/
├── src/
│   ├── app/
│   ├── engine/
│   └── .streamlit/
├── tests/
├── validation/
├── requirements.txt
├── LICENSE
├── LICENSE-DATA
└── CITATION.cff
```

## Requirements

The publication release was tested with:

- Python 3.13.14
- biopython 1.87
- numpy 2.5.1
- pandas 3.0.3
- scipy 1.18.1
- streamlit 1.59.0

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running the Streamlit application

### PowerShell

```powershell
$env:PYTHONPATH = ".\src;."
python -m streamlit run .\src\app\Home.py
```

### Linux/macOS

```bash
export PYTHONPATH="./src:."
python -m streamlit run ./src/app/Home.py
```

## Reproducibility

Key validation results reproduced in this release include:

- Exact evolutionary substitution recovery: **13/22 (59.1%)**.
- Composition-aware enrichment: **>3.4-fold; empirical p < 0.001**.
- Literature-blind WHERE benchmark: **5/15 positions recovered in Top30**.
- Formal WHERE benchmark: expected random recovery **1.72**, enrichment **2.91-fold**, **p = 0.01852**.
- Conditional WHAT validation: **4/5 exact beneficial substitutions recovered within WHAT Top5**.
- End-to-end recovery: **4/15 (26.7%)**.
- Coordinate robustness: **20/20 stress tests passed**.

The formal WHERE null model uses **262 structurally evaluable reference positions**. The reduction from 290 total reference positions to the WHERE Top30 corresponds to an **89.7% search-space reduction**.

Some earlier evolutionary-only validation modules retain their original historical **243-position eligible universe**. These analyses are preserved as frozen reproducibility components and are distinct from the final formal WHERE benchmark.

## Test suite

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

The current publication release passes **66 / 66 tests**.

## Data provenance

The project incorporates or derives information from external scientific resources including UniProtKB, experimentally determined Protein Data Bank structures, and published PET-hydrolase studies.

Third-party resources remain subject to the licenses and terms of their original providers.

Project-generated data and derived tables are covered by `LICENSE-DATA`.

## Citation

A formal citation for the associated manuscript and archival Zenodo release will be added when available.

Current manuscript title:

**PETase Engineering Atlas: A Group-Aware Evolutionary Framework for Prioritizing Mutation Hypotheses in PET Hydrolases**

## License

Source code is released under the **MIT License**.

Project-generated datasets and derived research outputs are released under **CC BY 4.0**, except where third-party licensing terms apply.

## Author

**Martín Alfredo Vargas Fernández**

## Repository

Source code and reproducibility resources are available at:
https://github.com/martinvargasfernandez/PETase-Engineering-Atlas

## Archived release and citation

The frozen publication release **v1.0.0** is permanently archived in Zenodo:

- Version DOI: https://doi.org/10.5281/zenodo.22642100
- Concept DOI: https://doi.org/10.5281/zenodo.22642098

For reproducibility of the analyses associated with the accompanying study, please cite the version-specific DOI.

Suggested software citation:

Vargas Fernández, M. A. (2026). *PETase Engineering Atlas* (Version v1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22642100


