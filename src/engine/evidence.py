from engine.atlas import load_master_table


def get_position_evidence(position: int) -> dict:
    """
    Return all currently available global evidence for one IsPETase position.
    """
    df = load_master_table()

    match = df[df["IsPETase_position"] == position]

    if match.empty:
        return {}

    row = match.iloc[0]

    family_consensus = {}

    for col in df.columns:
        if (
            col.endswith("_consensus")
            and col not in [
                "Global_consensus",
                "Major_consensus",
                "Different_family_consensus",
            ]
        ):
            family_name = col.replace("_consensus", "")
            family_consensus[family_name] = row.get(col, None)

    evidence = {
        "position": int(row.get("IsPETase_position")),
        "reference_residue": row.get("IsPETase_residue"),
        "global_consensus": row.get("Global_consensus"),
        "global_conservation": row.get("Global_conservation"),
        "fvi": row.get("FVI"),
        "consensus_residues": row.get("Consensus_residues"),
        "known_mutations": row.get("Known_mutations"),
        "mutation_evidence": row.get("Mutation_evidence"),
        "family_consensus": family_consensus,
    }

    return evidence