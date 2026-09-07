import pandas as pd

from engine.evidence import get_position_evidence
from engine.atlas import load_master_table


def _is_missing(value) -> bool:
    """
    Return True if a value should be treated as missing.
    """
    return pd.isna(value) or value in ["", "nan", "NaN", None]


def _count_consensus_residues(consensus_residues) -> int:
    """
    Count the number of distinct consensus residues.
    """
    if _is_missing(consensus_residues):
        return 0

    return len([
        residue.strip()
        for residue in str(consensus_residues).split(",")
        if residue.strip()
    ])


def calculate_atlas_evidence_score(position: int) -> dict:
    """
    Calculate the current Atlas Evidence Score for one position.
    """
    evidence = get_position_evidence(position)

    if not evidence:
        return {}

    score = 0
    components = []

    fvi = evidence.get("fvi", 0)
    conservation = evidence.get("global_conservation", None)
    mutation_evidence = str(evidence.get("mutation_evidence", "NO")).upper()
    consensus_count = _count_consensus_residues(
        evidence.get("consensus_residues")
    )

    if fvi >= 5:
        score += 4
        components.append("High family variability: +4")
    elif fvi >= 3:
        score += 2
        components.append("Moderate family variability: +2")

    if mutation_evidence == "YES":
        score += 3
        components.append("Published mutation evidence: +3")

    if conservation is not None and conservation < 30:
        score += 2
        components.append("Low global conservation: +2")

    if consensus_count >= 4:
        score += 1
        components.append("Multiple family consensus residues: +1")

    score = min(score, 10)

    return {
        "position": position,
        "score": score,
        "max_score": 10,
        "components": components,
        "evidence": evidence,
    }


def rank_all_positions() -> pd.DataFrame:
    """
    Rank all IsPETase positions using the Atlas Evidence Score.
    """
    df = load_master_table()

    rows = []

    for position in df["IsPETase_position"].dropna().astype(int):
        result = calculate_atlas_evidence_score(position)

        if not result:
            continue

        evidence = result["evidence"]

        rows.append(
            {
                "IsPETase_position": position,
                "IsPETase_residue": evidence.get("reference_residue"),
                "Global_consensus": evidence.get("global_consensus"),
                "Global_conservation": evidence.get("global_conservation"),
                "FVI": evidence.get("fvi"),
                "Consensus_residues": evidence.get("consensus_residues"),
                "Known_mutations": evidence.get("known_mutations"),
                "Mutation_evidence": evidence.get("mutation_evidence"),
                "Atlas_Evidence_Score": result["score"],
                "Score_components": "; ".join(result["components"]),
            }
        )

    ranked = pd.DataFrame(rows)

    return ranked.sort_values(
        ["Atlas_Evidence_Score", "FVI"],
        ascending=False
    ).reset_index(drop=True)