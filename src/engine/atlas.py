import pandas as pd
from . import paths


def load_tsv(path):
    """
    Load a TSV file as a pandas DataFrame.
    """
    return pd.read_csv(path, sep="\t")


def load_master_table():
    """
    Load the master IsPETase-position table.
    """
    return load_tsv(paths.MASTER_TABLE)


def count_yes(series):
    """
    Count explicit YES values in a column.
    """
    return int(series.astype(str).str.upper().eq("YES").sum())


def get_atlas_summary():
    """
    Return basic summary metrics for the PETase Engineering Atlas.
    """
    df = load_master_table()

    summary = {
        "reference_positions": len(df),
        "high_fvi_positions": int((df["FVI"] >= 3).sum()) if "FVI" in df.columns else 0,
        "positions_with_known_mutations": int(
            df["Known_mutations"].notna().sum()
        ) if "Known_mutations" in df.columns else 0,
        "positions_with_mutation_evidence": count_yes(
            df["Mutation_evidence"]
        ) if "Mutation_evidence" in df.columns else 0,
    }

    return summary