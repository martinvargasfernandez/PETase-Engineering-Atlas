class AtlasPosition:
    """
    Conceptual read-only wrapper around engine.residue.Residue representing
    an evolutionary coordinate in the PETase Engineering Atlas.
    """

    COORDINATE_SYSTEM = "IsPETase_v1"

    def __init__(self, position_id: int):
        from engine.residue import Residue
        self._residue = Residue(position_id)

    @property
    def atlas_position_id(self) -> int:
        return self._residue.position

    @property
    def coordinate_system(self) -> str:
        return self.COORDINATE_SYSTEM

    @property
    def IsPETase_position(self) -> int:
        return self._residue.position

    @property
    def IsPETase_residue(self) -> str:
        return self._residue.reference_residue

    @property
    def global_consensus(self) -> str:
        return self._residue.global_consensus

    @property
    def global_conservation(self) -> float:
        return self._residue.global_conservation

    @property
    def fvi(self) -> int:
        return self._residue.fvi

    @property
    def consensus_residues(self):
        return self._residue.consensus_residues

    @property
    def known_mutations(self):
        return self._residue.known_mutations

    @property
    def mutation_evidence(self):
        return self._residue.mutation_evidence

    @property
    def family_consensus(self) -> dict:
        return self._residue.family_consensus

    @property
    def atlas_evidence_score(self) -> int:
        return self._residue.atlas_evidence_score

    @property
    def max_score(self) -> int:
        return self._residue.max_score

    @property
    def score_components(self) -> list:
        return self._residue.score_components

    @property
    def priority(self) -> str:
        return self._residue.priority

    @property
    def interpretation(self) -> str:
        return self._residue.interpretation

    def describe(self) -> str:
        """
        Returns a concise and factual textual description of the position.
        """
        return f"AtlasPosition {self.atlas_position_id} ({self.IsPETase_residue}) | Coordinate System: {self.coordinate_system} | Score: {self.atlas_evidence_score}/{self.max_score} | Priority: {self.priority}"

    def _clean_value(self, value):
        import math

        if value is None:
            return None

        if isinstance(value, dict):
            return {
                self._clean_value(key): self._clean_value(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [self._clean_value(item) for item in value]

        try:
            if isinstance(value, float) and math.isnan(value):
                return None
        except TypeError:
            pass

        if hasattr(value, "item"):
            try:
                return value.item()
            except (TypeError, ValueError):
                pass

        return value

    def to_dict(self) -> dict:
        """
        Export the AtlasPosition object as a dictionary of clean Python types.
        """
        raw = {
            "atlas_position_id": self.atlas_position_id,
            "coordinate_system": self.coordinate_system,
            "IsPETase_position": self.IsPETase_position,
            "IsPETase_residue": self.IsPETase_residue,
            "global_consensus": self.global_consensus,
            "global_conservation": self.global_conservation,
            "fvi": self.fvi,
            "consensus_residues": self.consensus_residues,
            "known_mutations": self.known_mutations,
            "mutation_evidence": self.mutation_evidence,
            "family_consensus": self.family_consensus,
            "atlas_evidence_score": self.atlas_evidence_score,
            "max_score": self.max_score,
            "score_components": self.score_components,
            "priority": self.priority,
            "interpretation": self.interpretation,
        }
        return self._clean_value(raw)

    def to_json(self) -> str:
        """
        Serializes the cleaned dictionary representation to a JSON string with sorted keys.
        """
        import json
        return json.dumps(self.to_dict(), sort_keys=True)