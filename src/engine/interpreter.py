from engine.ranking import calculate_atlas_evidence_score


def interpret_position(position: int) -> dict:
    """
    Generate rule-based scientific interpretation for one IsPETase position.
    """

    result = calculate_atlas_evidence_score(position)

    if not result:
        return {}

    evidence = result["evidence"]
    score = result["score"]

    fvi = evidence.get("fvi", 0)
    conservation = evidence.get("global_conservation", None)
    mutation_evidence = str(
        evidence.get("mutation_evidence", "NO")
    ).upper()

    known_mutations = evidence.get("known_mutations")
    consensus_residues = evidence.get("consensus_residues")

    # Unified Atlas priority
    if score >= 8:
        priority = "High"
    elif score >= 5:
        priority = "Medium"
    else:
        priority = "Low"

    statements = []

    if fvi >= 5:
        statements.append(
            "This position shows strong family-level variability, suggesting substantial evolutionary flexibility among PETase families."
        )

    elif fvi >= 3:
        statements.append(
            "This position shows moderate family-level variability and may be relevant for engineering depending on its structural context."
        )

    else:
        statements.append(
            "This position shows limited family-level variability, suggesting stronger evolutionary conservation."
        )

    if conservation is not None:

        if conservation < 30:
            statements.append(
                "The low global conservation indicates that multiple amino acid states are tolerated across the current sequence set."
            )

        elif conservation >= 70:
            statements.append(
                "The high global conservation suggests that mutations at this site should be interpreted cautiously."
            )

    if mutation_evidence == "YES":
        statements.append(
            f"Experimental mutation evidence is already available for this position: {known_mutations}."
        )

    else:
        statements.append(
            "No published mutation evidence is currently registered for this position in the Atlas."
        )

    if consensus_residues:
        statements.append(
            f"The observed family consensus residues are: {consensus_residues}."
        )

    return {
        "position": position,
        "priority": priority,
        "score": score,
        "max_score": result["max_score"],
        "interpretation": " ".join(statements),
        "components": result["components"],
    }