import pandas as pd
from . import paths


def load_tsv(path):
    """
    Load a TSV file as a pandas DataFrame.
    """
    return pd.read_csv(path, sep="\t")


def load_family_assignments():
    """
    Load family assignments for PETase-like sequences.
    """
    return load_tsv(paths.FAMILY_ASSIGNMENTS)


def load_family_definitions():
    """
    Load family definitions.
    """
    return load_tsv(paths.FAMILY_DEFINITIONS)


def load_family_consensus_summary():
    """
    Load family-level consensus summary.
    """
    return load_tsv(paths.FAMILY_CONSENSUS_SUMMARY)


def load_family_variability_index():
    """
    Load family variability index table.
    """
    return load_tsv(paths.FAMILY_VARIABILITY_INDEX)


def load_global_family_consensus_matrix():
    """
    Load the position-by-family consensus matrix.
    """
    return load_tsv(paths.GLOBAL_FAMILY_CONSENSUS_MATRIX)


def get_family_summary():
    """
    Return basic family-level summary statistics.
    """
    assignments = load_family_assignments()

    if "family_name" not in assignments.columns:
        return pd.DataFrame()

    summary = (
        assignments["family_name"]
        .value_counts()
        .reset_index()
    )

    summary.columns = ["family_name", "sequence_count"]

    return summary