class EngineeringReport:
    """
    Scientific report for a single engineering position.
    """

    def __init__(self, residue, proposals):
        self.position = residue.position
        self.reference_residue = residue.reference_residue
        self.residue = residue

        self.atlas_evidence_score = residue.atlas_evidence_score
        self.priority = residue.priority
        self.interpretation = residue.interpretation

        self.proposals = sorted(
            proposals,
            key=lambda p: p.proposal_score,
            reverse=True,
        )

    @property
    def best_mutation(self):
        if not self.proposals:
            return None
        return self.proposals[0]

    @property
    def alternative_mutations(self):
        if len(self.proposals) <= 1:
            return []
        return self.proposals[1:]

    def to_dict(self):
        return {
            "position": self.position,
            "reference_residue": self.reference_residue,
            "atlas_evidence_score": self.atlas_evidence_score,
            "priority": self.priority,
            "interpretation": self.interpretation,
            "best_mutation": (
                self.best_mutation.to_dict()
                if self.best_mutation
                else None
            ),
            "alternative_mutations": [
                m.to_dict() for m in self.alternative_mutations
            ],
        }