def interpret_engineering_decision(decision_result: dict) -> str:
    """
    Generates a scientific interpretation for an engineering decision.
    """

    atlas_score = decision_result.get("atlas_evidence_score")
    engineering_priority = decision_result.get("engineering_priority")
    enzyme_name = decision_result.get("enzyme_name")
    position = decision_result.get("position")
    reference_residue = decision_result.get("reference_residue")
    reasons = decision_result.get("reasons", [])

    label = f"{reference_residue}{position}"

    has_global_support = atlas_score is not None and atlas_score > 0
    has_case_support = len(reasons) > 1

    if has_global_support and has_case_support:
        return (
            f"{label} is supported by both global Atlas evidence and "
            f"{enzyme_name}-specific evidence. This residue should be considered "
            f"a strong candidate for protein engineering."
        )

    if not has_global_support and has_case_support:
        return (
            f"{label} is not prioritized by the global Atlas Evidence Score, "
            f"but shows relevant enzyme-specific support in {enzyme_name}. "
            f"This residue may be important in this particular protein context."
        )

    if has_global_support and not has_case_support:
        return (
            f"{label} is supported by global Atlas evidence, but currently lacks "
            f"strong enzyme-specific evidence in {enzyme_name}. It remains a candidate, "
            f"but should be evaluated structurally before mutation."
        )

    return (
        f"{label} currently has limited global and enzyme-specific support. "
        f"It should not be prioritized unless additional evidence emerges."
    )