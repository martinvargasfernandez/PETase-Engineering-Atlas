from engine.evidence import get_position_evidence
from engine.ranking import calculate_atlas_evidence_score
from engine.interpreter import interpret_position


class Residue:
    """
    Scientific object representing one IsPETase reference position
    in the PETase Engineering Atlas.
    """

    def __init__(self, position: int):
        self.position = int(position)
        self.evidence = get_position_evidence(self.position)

        if not self.evidence:
            raise ValueError(f"Position {self.position} not found in the Atlas.")

        self.score_result = calculate_atlas_evidence_score(self.position)
        self.interpretation_result = interpret_position(self.position)

    @property
    def reference_residue(self):
        return self.evidence.get("reference_residue")

    @property
    def global_consensus(self):
        return self.evidence.get("global_consensus")

    @property
    def global_conservation(self):
        return self.evidence.get("global_conservation")

    @property
    def fvi(self):
        return self.evidence.get("fvi")

    @property
    def consensus_residues(self):
        return self.evidence.get("consensus_residues")

    @property
    def known_mutations(self):
        return self.evidence.get("known_mutations")

    @property
    def mutation_evidence(self):
        return self.evidence.get("mutation_evidence")

    @property
    def family_consensus(self):
        return self.evidence.get("family_consensus", {})

    @property
    def atlas_evidence_score(self):
        return self.score_result.get("score")

    @property
    def max_score(self):
        return self.score_result.get("max_score")

    @property
    def score_components(self):
        return self.score_result.get("components", [])

    @property
    def priority(self):
        return self.interpretation_result.get("priority")

    @property
    def interpretation(self):
        return self.interpretation_result.get("interpretation")

    def to_dict(self):
        """
        Export the residue object as a dictionary.
        """
        return {
            "position": self.position,
            "reference_residue": self.reference_residue,
            "global_consensus": self.global_consensus,
            "global_conservation": self.global_conservation,
            "fvi": self.fvi,
            "consensus_residues": self.consensus_residues,
            "known_mutations": self.known_mutations,
            "mutation_evidence": self.mutation_evidence,
            "atlas_evidence_score": self.atlas_evidence_score,
            "max_score": self.max_score,
            "priority": self.priority,
            "interpretation": self.interpretation,
        }