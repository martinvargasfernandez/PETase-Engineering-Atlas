import math


def is_missing(value):
    if value is None:
        return True

    try:
        if isinstance(value, float) and math.isnan(value):
            return True
    except TypeError:
        pass

    value = str(value).strip()

    if value.lower() in {"", "nan", "none", "null", "na", "n/a", "-"}:
        return True

    return False


class ProposalScoringEngine:
    """
    Scores Mutation proposals using residue-level Atlas evidence.
    """

    def score(self, mutation, residue=None):
        target = mutation
        if residue is None:
            if hasattr(mutation, "residue") and hasattr(mutation, "mutation"):
                residue = mutation.residue
                target = mutation.mutation
            else:
                raise ValueError("Residue reference must be provided or available on the candidate.")

        components = {}

        fvi = getattr(residue, "fvi", 0)
        known_mutations = getattr(residue, "known_mutations", None)
        evidence = getattr(target, "evidence", {}) or {}
        sources = getattr(target, "sources", []) or []

        supporting_families = evidence.get("supporting_families", [])

        components["family_support"] = len(supporting_families)
        components["fvi"] = int(fvi) if not is_missing(fvi) else 0
        components["known_mutation_support"] = (
            3 if "known_mutation" in sources or not is_missing(known_mutations) else 0
        )
        components["chemical_plausibility"] = (
            1 if target.chemical_change() == "Conservative" else 0
        )

        total_score = sum(components.values())

        if total_score >= 8:
            priority = "High"
        elif total_score >= 4:
            priority = "Medium"
        else:
            priority = "Low"

        target.proposal_score = total_score
        target.proposal_priority = priority
        target.evidence["proposal_score_components"] = components

        return mutation