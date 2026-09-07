import json
from engine.mapping_status import MappingStatus

class MappedResidue:
    """
    Scientific Entity: MappedResidue

    Represents only the relationship between:
    - one residue position in a StudySequence;
    - one AtlasPosition, when a mapping exists.

    Responsible only for:
    - validating local residue coordinates and alignment states
    - delegating reference and sequence attributes
    - serializing mapping records

    It does NOT perform:
    - alignment
    - family classification
    - project persistence
    - docking
    - molecular dynamics
    - Atlas queries

    Warnings Policy:
        The warnings property is an append-only immutable sequence.
        Warnings are not restricted to plain strings and may later become structured 
        dictionaries containing fields such as 'code' and 'message'.
    """

    def __init__(
        self,
        study_sequence,
        mapping_status,
        study_position: int = None,
        study_residue: str = None,
        atlas_position = None,
        mapping_confidence: float = None,
        warnings: list = None
    ):
        # Duck typing validation for study_sequence
        if not hasattr(study_sequence, "study_id") or not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")

        self._study_sequence = study_sequence
        
        # 1. Validate mapping status (accepts only MappingStatus Enum)
        if not isinstance(mapping_status, MappingStatus):
            raise TypeError("mapping_status must be a MappingStatus Enum member.")
        self._mapping_status = mapping_status

        # 2. Validate confidence
        if mapping_confidence is not None:
            try:
                conf = float(mapping_confidence)
                if not (0.0 <= conf <= 1.0):
                    raise ValueError()
                self._mapping_confidence = conf
            except (TypeError, ValueError):
                raise ValueError("mapping_confidence must be between 0.0 and 1.0.")
        else:
            self._mapping_confidence = None

        # 3. Validate mapping state consistency and reuse shared validation library
        from engine.sequence_validation import validate_amino_acid
        
        acc_warnings = []
        normalized_residue = None

        if self._mapping_status in (MappingStatus.EXACT_MATCH, MappingStatus.SUBSTITUTION):
            if study_position is None or study_position <= 0:
                raise ValueError(f"study_position must be a positive integer for status '{self._mapping_status.value}'.")
            if study_residue is None:
                raise ValueError(f"study_residue must be a single character for status '{self._mapping_status.value}'.")
            
            try:
                normalized_residue, aa_warnings = validate_amino_acid(study_residue)
                acc_warnings.extend(aa_warnings)
            except ValueError:
                raise ValueError(f"Invalid amino acid character '{study_residue}'.")
                
            # Duck typing validation for atlas_position
            if not hasattr(atlas_position, "atlas_position_id") or not hasattr(atlas_position, "IsPETase_residue"):
                raise TypeError(f"atlas_position must implement the AtlasPosition interface for status '{self._mapping_status.value}'.")
            
            # Check residue match vs substitution consistency
            ref_res = atlas_position.IsPETase_residue
            if self._mapping_status == MappingStatus.EXACT_MATCH and normalized_residue != ref_res:
                raise ValueError("study_residue must match reference residue for status 'exact_match'.")
            if self._mapping_status == MappingStatus.SUBSTITUTION and normalized_residue == ref_res:
                raise ValueError("study_residue must differ from reference residue for status 'substitution'.")

        elif self._mapping_status == MappingStatus.INSERTION:
            if study_position is None or study_position <= 0:
                raise ValueError("study_position must be a positive integer for status 'insertion'.")
            if study_residue is None:
                raise ValueError("study_residue must be a single character for status 'insertion'.")
            try:
                normalized_residue, aa_warnings = validate_amino_acid(study_residue)
                acc_warnings.extend(aa_warnings)
            except ValueError:
                raise ValueError(f"Invalid amino acid character '{study_residue}'.")
            if atlas_position is not None:
                raise ValueError("atlas_position must be None for status 'insertion'.")

        elif self._mapping_status == MappingStatus.DELETION:
            if study_position is not None or study_residue is not None:
                raise ValueError("study_position and study_residue must be None for status 'deletion'.")
            if not hasattr(atlas_position, "atlas_position_id") or not hasattr(atlas_position, "IsPETase_residue"):
                raise TypeError("atlas_position must implement the AtlasPosition interface for status 'deletion'.")

        elif self._mapping_status == MappingStatus.UNMAPPED:
            if study_position is None or study_position <= 0:
                raise ValueError("study_position must be a positive integer for status 'unmapped'.")
            if study_residue is None:
                raise ValueError("study_residue must be a single character for status 'unmapped'.")
            try:
                normalized_residue, aa_warnings = validate_amino_acid(study_residue)
                acc_warnings.extend(aa_warnings)
            except ValueError:
                raise ValueError(f"Invalid amino acid character '{study_residue}'.")
            if atlas_position is not None:
                raise ValueError("atlas_position must be None for status 'unmapped'.")

        self._study_position = study_position
        self._study_residue = normalized_residue
        self._atlas_position = atlas_position
        
        # Merge amino-acid validation warnings with supplied warnings
        merged_warnings = list(warnings) if warnings is not None else []
        merged_warnings.extend(acc_warnings)
        self._warnings = merged_warnings

    @property
    def study_sequence(self):
        return self._study_sequence

    @property
    def study_id(self) -> str:
        return self._study_sequence.study_id

    @property
    def study_position(self) -> int:
        return self._study_position

    @property
    def study_residue(self) -> str:
        return self._study_residue

    @property
    def atlas_position(self):
        return self._atlas_position

    @property
    def atlas_position_id(self) -> int:
        if self._atlas_position is not None:
            return self._atlas_position.atlas_position_id
        return None

    @property
    def atlas_reference_residue(self) -> str:
        if self._atlas_position is not None:
            return self._atlas_position.IsPETase_residue
        return None

    @property
    def mapping_status(self) -> MappingStatus:
        return self._mapping_status

    @property
    def mapping_confidence(self) -> float:
        return self._mapping_confidence

    @property
    def warnings(self) -> tuple:
        return tuple(self._warnings)

    @property
    def has_reference(self) -> bool:
        return self._atlas_position is not None

    @property
    def is_mapped(self) -> bool:
        return self._mapping_status in (MappingStatus.EXACT_MATCH, MappingStatus.SUBSTITUTION)

    @property
    def is_exact_match(self) -> bool:
        return self._mapping_status == MappingStatus.EXACT_MATCH

    @property
    def is_substitution(self) -> bool:
        return self._mapping_status == MappingStatus.SUBSTITUTION

    @property
    def is_insertion(self) -> bool:
        return self._mapping_status == MappingStatus.INSERTION

    @property
    def is_deletion(self) -> bool:
        return self._mapping_status == MappingStatus.DELETION

    @property
    def is_unmapped(self) -> bool:
        return self._mapping_status == MappingStatus.UNMAPPED

    @property
    def query_mapping_state(self) -> str | None:
        if self._mapping_status in (MappingStatus.EXACT_MATCH, MappingStatus.SUBSTITUTION):
            return "mapped"
        elif self._mapping_status == MappingStatus.INSERTION:
            return "insertion"
        elif self._mapping_status == MappingStatus.UNMAPPED:
            return "unmapped"
        return None

    def describe(self) -> str:
        """
        Returns a concise and factual description of the mapping relationship.
        """
        target = f"AtlasPosition {self.atlas_position_id}" if self.atlas_position_id is not None else "None"
        local = f"{self.study_residue}{self.study_position}" if self.study_position is not None else "Gap"
        conf_part = f" | Confidence: {self.mapping_confidence}" if self.mapping_confidence is not None else ""
        return f"MappedResidue {local} -> {target} | Status: {self.mapping_status.value}{conf_part}"

    def to_dict(self) -> dict:
        """
        Export the MappedResidue object as a dictionary of native Python values.
        """
        return {
            "entity": "MappedResidue",
            "schema_version": 1,
            "study_id": self.study_id,
            "study_position": self.study_position,
            "study_residue": self.study_residue,
            "atlas_position_id": self.atlas_position_id,
            "atlas_reference_residue": self.atlas_reference_residue,
            "mapping_status": self.mapping_status.value,
            "mapping_confidence": self.mapping_confidence,
            "is_mapped": self.is_mapped,
            "is_exact_match": self.is_exact_match,
            "is_substitution": self.is_substitution,
            "is_insertion": self.is_insertion,
            "is_deletion": self.is_deletion,
            "is_unmapped": self.is_unmapped,
            "query_mapping_state": self.query_mapping_state,
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        """
        Serializes the dictionary representation to a JSON string.
        """
        return json.dumps(self.to_dict(), sort_keys=True)
