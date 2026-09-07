from pathlib import Path
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ATLAS_DIR = PROJECT_ROOT / "atlas_v3"
FAMILIES_DIR = ATLAS_DIR / "families"


FILES = {
    "master": ATLAS_DIR / "atlas_v3_master_position_table.tsv",
    "candidates": ATLAS_DIR / "evolutionary_candidates.tsv",
    "validated_candidates": ATLAS_DIR / "evolutionary_candidates_with_mutation_evidence.tsv",
    "known_mutations": ATLAS_DIR / "known_mutations_atlas_v3.tsv",
    "family_assignments": FAMILIES_DIR / "petase_atlas_v3_family_assignments.tsv",
    "family_consensus_summary": FAMILIES_DIR / "family_consensus_summary.tsv",
    "family_variability": FAMILIES_DIR / "family_variability_index.tsv",
    "family_consensus_matrix": FAMILIES_DIR / "global_family_consensus_matrix.tsv",
}


@st.cache_data
def load_tsv(path: Path) -> pd.DataFrame:
    """
    Load a TSV file with basic error handling.
    """
    if not path.exists():
        st.warning(f"File not found: {path}")
        return pd.DataFrame()

    return pd.read_csv(path, sep="\t")


def load_master_table() -> pd.DataFrame:
    return load_tsv(FILES["master"])


def load_candidates() -> pd.DataFrame:
    return load_tsv(FILES["candidates"])


def load_validated_candidates() -> pd.DataFrame:
    return load_tsv(FILES["validated_candidates"])


def load_known_mutations() -> pd.DataFrame:
    return load_tsv(FILES["known_mutations"])


def load_family_assignments() -> pd.DataFrame:
    return load_tsv(FILES["family_assignments"])


def load_family_consensus_summary() -> pd.DataFrame:
    return load_tsv(FILES["family_consensus_summary"])


def load_family_variability() -> pd.DataFrame:
    return load_tsv(FILES["family_variability"])


def load_family_consensus_matrix() -> pd.DataFrame:
    return load_tsv(FILES["family_consensus_matrix"])