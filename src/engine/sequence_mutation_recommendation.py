"""
Scientific Entity: SequenceMutationRecommendation

Read-only value object representing one prioritized mutation candidate for a specific
submitted (query) sequence, expressed in query numbering.

Each recommendation is derived exclusively from global Atlas evidence
(family variability, family/global consensus, known mutations, Atlas evidence score)
and is linked to both the query coordinate system and the Atlas coordinate system
for full provenance.

Stage 5.4 — Sequence Analysis Engine
"""


class SequenceMutationRecommendation:
    """
    A single mutation recommendation for a submitted sequence, expressed in query numbering.

    Fields:
        study_id                : Identifier of the submitted study sequence.
        query_position          : Residue position in the submitted sequence (1-indexed).
        query_residue           : Current amino acid at that query position.
        atlas_position          : Corresponding IsPETase Atlas position.
        atlas_reference_residue : Reference amino acid at the Atlas position.
        proposed_mutant         : Proposed mutant amino acid.
        query_notation          : Mutation in query numbering (e.g. "K285A").
        atlas_notation          : Mutation in Atlas numbering (e.g. "R280A").
        proposal_score          : Integer proposal score (global Atlas evidence only).
        proposal_priority       : Priority category ("High", "Medium", or "Low").
        sources                 : Evidence generators that contributed this proposal.
        global_evidence         : Dict with fvi, global_conservation, global_consensus,
                                  known_mutations — global Atlas evidence only.
        supporting_families     : Protein families supporting this proposal via consensus.
        known_mutation_evidence : Known mutation string if this proposal is experimentally
                                  reported, or None.
        alternatives            : Alternative proposed mutants at this position, each as
                                  a dict with query_notation, atlas_notation, proposed_mutant,
                                  sources, proposal_score, proposal_priority.
        exclusion_reason        : Reason string if this record was excluded; otherwise None.
    """

    __slots__ = (
        "study_id",
        "query_position",
        "query_residue",
        "atlas_position",
        "atlas_reference_residue",
        "proposed_mutant",
        "query_notation",
        "atlas_notation",
        "proposal_score",
        "proposal_priority",
        "sources",
        "global_evidence",
        "supporting_families",
        "known_mutation_evidence",
        "alternatives",
        "exclusion_reason",
    )

    def __init__(
        self,
        study_id: str,
        query_position: int,
        query_residue: str,
        atlas_position: int,
        atlas_reference_residue: str,
        proposed_mutant: str,
        query_notation: str,
        atlas_notation: str,
        proposal_score: int,
        proposal_priority: str,
        sources: list,
        global_evidence: dict,
        supporting_families: list,
        known_mutation_evidence,
        alternatives: list,
        exclusion_reason=None,
    ):
        self.study_id = str(study_id)
        self.query_position = int(query_position)
        self.query_residue = str(query_residue)
        self.atlas_position = int(atlas_position)
        self.atlas_reference_residue = str(atlas_reference_residue)
        self.proposed_mutant = str(proposed_mutant)
        self.query_notation = str(query_notation)
        self.atlas_notation = str(atlas_notation)
        self.proposal_score = int(proposal_score)
        self.proposal_priority = str(proposal_priority)
        self.sources = list(sources) if sources is not None else []
        self.global_evidence = dict(global_evidence) if global_evidence is not None else {}
        self.supporting_families = list(supporting_families) if supporting_families is not None else []
        self.known_mutation_evidence = known_mutation_evidence
        self.alternatives = list(alternatives) if alternatives is not None else []
        self.exclusion_reason = exclusion_reason

    def to_dict(self) -> dict:
        """
        Returns a complete, serializable dictionary representation of this recommendation.
        All fields are included to support auditing and tabular export.
        """
        return {
            "study_id": self.study_id,
            "query_position": self.query_position,
            "query_residue": self.query_residue,
            "atlas_position": self.atlas_position,
            "atlas_reference_residue": self.atlas_reference_residue,
            "proposed_mutant": self.proposed_mutant,
            "query_notation": self.query_notation,
            "atlas_notation": self.atlas_notation,
            "proposal_score": self.proposal_score,
            "proposal_priority": self.proposal_priority,
            "sources": self.sources,
            "global_evidence": self.global_evidence,
            "supporting_families": self.supporting_families,
            "known_mutation_evidence": self.known_mutation_evidence,
            "alternatives": self.alternatives,
            "exclusion_reason": self.exclusion_reason,
        }

    def __repr__(self) -> str:
        return (
            f"SequenceMutationRecommendation("
            f"study_id={self.study_id!r}, "
            f"query_notation={self.query_notation!r}, "
            f"atlas_notation={self.atlas_notation!r}, "
            f"score={self.proposal_score}, "
            f"priority={self.proposal_priority!r})"
        )
