class ProposalInterpreter:
    """
    Generates human-readable scientific explanations for mutation proposals.
    """

    def interpret(self, candidate):
        reasons = []

        family_support = getattr(candidate, "supporting_families", [])
        score_components = getattr(candidate, "proposal_score_components", {})
        priority = getattr(candidate, "proposal_priority", "Unknown")

        fvi = score_components.get("fvi", 0)
        known = score_components.get("known_mutation_support", 0)
        chemistry = score_components.get("chemical_plausibility", 0)

        if family_support:
            reasons.append(
                f"Observed as consensus residue in {len(family_support)} protein family/families."
            )

        if fvi >= 4:
            reasons.append(
                f"Position shows high evolutionary variability (FVI = {fvi})."
            )
        elif fvi > 0:
            reasons.append(
                f"Position shows measurable evolutionary variability (FVI = {fvi})."
            )
        else:
            reasons.append(
                "Position shows low evolutionary variability."
            )

        if known > 0:
            reasons.append(
                "Previous mutation evidence is available for this position."
            )
        else:
            reasons.append(
                "No previous mutation evidence is currently available for this position."
            )

        if chemistry > 0:
            reasons.append(
                "The substitution is chemically conservative."
            )
        else:
            reasons.append(
                "The substitution is chemically non-conservative and may require structural inspection."
            )

        return {
            "candidate": candidate.label,
            "proposal_priority": priority,
            "interpretation": " ".join(reasons),
            "reasons": reasons,
        }