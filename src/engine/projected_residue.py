import json
import copy
from engine.mapping_status import MappingStatus

def _defensive_copy(val):
    """
    Returns a deep, defensive copy of collections or returns scalar values directly.
    Converts numpy scalars to standard Python scalars recursively using .item() if available.
    """
    if isinstance(val, dict):
        return {k: _defensive_copy(v) for k, v in val.items()}
    elif isinstance(val, (list, tuple)):
        return [_defensive_copy(x) for x in val]
    elif hasattr(val, "item"):
        return val.item()
    return val

class ProjectedResidue:
    """
    Scientific Entity: ProjectedResidue

    A live, read-only projection representing one MappedResidue aligned with AtlasPosition evidence.
    Delegates all calls to the underlying MappedResidue and its associated AtlasPosition dynamically.
    Does not duplicate or cache state during construction.
    """

    def __init__(self, mapped_residue):
        # Duck typing interface validation
        if not hasattr(mapped_residue, "mapping_status") or not hasattr(mapped_residue, "study_id"):
            raise TypeError("mapped_residue must implement the MappedResidue interface.")
        self._mapped_residue = mapped_residue

    @property
    def study_id(self) -> str:
        return self._mapped_residue.study_id

    @property
    def study_position(self) -> int:
        return self._mapped_residue.study_position

    @property
    def study_residue(self) -> str:
        return self._mapped_residue.study_residue

    @property
    def mapping_status(self) -> MappingStatus:
        return self._mapped_residue.mapping_status

    @property
    def mapping_confidence(self) -> float:
        return self._mapped_residue.mapping_confidence

    @property
    def atlas_position_id(self) -> int:
        return self._mapped_residue.atlas_position_id

    @property
    def atlas_reference_residue(self) -> str:
        return self._mapped_residue.atlas_reference_residue

    @property
    def is_mapped(self) -> bool:
        return self._mapped_residue.is_mapped

    @property
    def warnings(self) -> tuple:
        return self._mapped_residue.warnings

    # --- Live read-only delegation of AtlasPosition evidence ---
    @property
    def global_consensus(self) -> str:
        if self._mapped_residue.atlas_position is not None:
            return self._mapped_residue.atlas_position.global_consensus
        return None

    @property
    def global_conservation(self) -> float:
        if self._mapped_residue.atlas_position is not None:
            return self._mapped_residue.atlas_position.global_conservation
        return None

    @property
    def fvi(self) -> int:
        if self._mapped_residue.atlas_position is not None:
            return self._mapped_residue.atlas_position.fvi
        return None

    @property
    def consensus_residues(self):
        if self._mapped_residue.atlas_position is not None:
            return _defensive_copy(self._mapped_residue.atlas_position.consensus_residues)
        return None

    @property
    def family_consensus(self) -> dict:
        if self._mapped_residue.atlas_position is not None:
            return _defensive_copy(self._mapped_residue.atlas_position.family_consensus)
        return {}

    @property
    def known_mutations(self):
        if self._mapped_residue.atlas_position is not None:
            return _defensive_copy(self._mapped_residue.atlas_position.known_mutations)
        return None

    @property
    def mutation_evidence(self):
        if self._mapped_residue.atlas_position is not None:
            return _defensive_copy(self._mapped_residue.atlas_position.mutation_evidence)
        return None

    @property
    def atlas_evidence_score(self) -> int:
        if self._mapped_residue.atlas_position is not None:
            return self._mapped_residue.atlas_position.atlas_evidence_score
        return None

    @property
    def max_score(self) -> int:
        if self._mapped_residue.atlas_position is not None:
            return self._mapped_residue.atlas_position.max_score
        return None

    @property
    def score_components(self) -> list:
        if self._mapped_residue.atlas_position is not None:
            return _defensive_copy(self._mapped_residue.atlas_position.score_components)
        return []

    @property
    def priority(self) -> str:
        if self._mapped_residue.atlas_position is not None:
            return self._mapped_residue.atlas_position.priority
        return None

    @property
    def interpretation(self) -> str:
        if self._mapped_residue.atlas_position is not None:
            return self._mapped_residue.atlas_position.interpretation
        return None

    @property
    def query_mapping_state(self) -> str | None:
        return self._mapped_residue.query_mapping_state

    def describe(self) -> str:
        """
        Concise scientific summary description.
        """
        local = f"{self.study_residue}{self.study_position}" if self.study_position else "Gap"
        target = f"AtlasPosition {self.atlas_position_id}" if self.atlas_position_id else "None"
        prio_part = f" | Priority: {self.priority}" if self.priority else ""
        return f"ProjectedResidue {local} -> {target} | Status: {self.mapping_status.value}{prio_part}"

    def to_dict(self) -> dict:
        """
        Serialize parameters to native dictionary format.
        """
        raw_dict = {
            "entity": "ProjectedResidue",
            "schema_version": 1,
            "study_id": self.study_id,
            "study_position": self.study_position,
            "study_residue": self.study_residue,
            "mapping_status": self.mapping_status.value,
            "mapping_confidence": self.mapping_confidence,
            "atlas_position_id": self.atlas_position_id,
            "atlas_reference_residue": self.atlas_reference_residue,
            "is_mapped": self.is_mapped,
            "query_mapping_state": self.query_mapping_state,
            "global_consensus": self.global_consensus,
            "global_conservation": self.global_conservation,
            "fvi": self.fvi,
            "consensus_residues": self.consensus_residues,
            "family_consensus": self.family_consensus,
            "known_mutations": self.known_mutations,
            "mutation_evidence": self.mutation_evidence,
            "atlas_evidence_score": self.atlas_evidence_score,
            "max_score": self.max_score,
            "score_components": self.score_components,
            "priority": self.priority,
            "interpretation": self.interpretation,
            "warnings": list(self.warnings)
        }
        return _defensive_copy(raw_dict)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
