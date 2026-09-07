import json

class MappingResult:
    """
    Scientific Entity: MappingResult

    Represents the complete result of aligning a StudySequence to a reference sequence.
    Exposes alignment parameters, matching scores, and is fully immutable.
    """

    def __init__(
        self,
        study_sequence,
        mapped_residues: list,
        alignment_score: float,
        exact_matches: int,
        substitutions: int,
        insertions: int,
        deletions: int,
        unmapped_residues: int,
        study_length: int,
        reference_length: int,
        alignment_length: int,
        alignment_method: str,
        scoring_parameters: dict,
        reference_sequence_hash: str,
        coordinate_system: str,
        reference_name: str,
        biopython_version: str,
        optimal_alignment_count: int,
        alignment_is_ambiguous: bool,
        warnings: list = None
    ):
        # 1. Verification of inputs via duck typing for StudySequence
        if not hasattr(study_sequence, "study_id") or not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")

        # 2. Verify all counts are non-negative integers
        for val, name in [
            (exact_matches, "exact_matches"),
            (substitutions, "substitutions"),
            (insertions, "insertions"),
            (deletions, "deletions"),
            (unmapped_residues, "unmapped_residues"),
            (study_length, "study_length"),
            (reference_length, "reference_length"),
            (alignment_length, "alignment_length"),
        ]:
            if not isinstance(val, int) or val < 0:
                raise ValueError(f"{name} must be a non-negative integer.")

        # 3. Strict global v1 validation checks
        if exact_matches + substitutions + insertions != study_length:
            raise ValueError(
                f"Inconsistent count: exact_matches ({exact_matches}) + substitutions ({substitutions}) + "
                f"insertions ({insertions}) != study_length ({study_length})."
            )
        if exact_matches + substitutions + deletions != reference_length:
            raise ValueError(
                f"Inconsistent count: exact_matches ({exact_matches}) + substitutions ({substitutions}) + "
                f"deletions ({deletions}) != reference_length ({reference_length})."
            )
        if alignment_length != exact_matches + substitutions + insertions + deletions:
            raise ValueError(
                f"Inconsistent count: alignment_length ({alignment_length}) != exact_matches ({exact_matches}) + "
                f"substitutions ({substitutions}) + insertions ({insertions}) + deletions ({deletions})."
            )
        if unmapped_residues != 0:
            raise ValueError("Inconsistent count: unmapped_residues must be 0 for global v1 mapper.")

        self._study_sequence = study_sequence
        self._mapped_residues = tuple(mapped_residues)
        self._alignment_score = float(alignment_score)
        self._exact_matches = exact_matches
        self._substitutions = substitutions
        self._insertions = insertions
        self._deletions = deletions
        self._unmapped_residues = unmapped_residues
        self._study_length = study_length
        self._reference_length = reference_length
        self._alignment_length = alignment_length
        self._alignment_method = str(alignment_method)
        self._scoring_parameters = dict(scoring_parameters)
        self._reference_sequence_hash = str(reference_sequence_hash)
        self._coordinate_system = str(coordinate_system)
        self._reference_name = str(reference_name)
        self._biopython_version = str(biopython_version)
        self._optimal_alignment_count = int(optimal_alignment_count) if optimal_alignment_count is not None else None
        self._alignment_is_ambiguous = bool(alignment_is_ambiguous)
        self._warnings = tuple(warnings) if warnings is not None else ()

    @property
    def study_sequence(self):
        return self._study_sequence

    @property
    def study_id(self) -> str:
        return self._study_sequence.study_id

    @property
    def mapped_residues(self) -> tuple:
        return self._mapped_residues

    @property
    def alignment_score(self) -> float:
        return self._alignment_score

    @property
    def exact_matches(self) -> int:
        return self._exact_matches

    @property
    def substitutions(self) -> int:
        return self._substitutions

    @property
    def insertions(self) -> int:
        return self._insertions

    @property
    def deletions(self) -> int:
        return self._deletions

    @property
    def unmapped_residues(self) -> int:
        return self._unmapped_residues

    @property
    def study_length(self) -> int:
        return self._study_length

    @property
    def reference_length(self) -> int:
        return self._reference_length

    @property
    def alignment_length(self) -> int:
        return self._alignment_length

    @property
    def alignment_method(self) -> str:
        return self._alignment_method

    @property
    def scoring_parameters(self) -> dict:
        return dict(self._scoring_parameters)

    @property
    def reference_sequence_hash(self) -> str:
        return self._reference_sequence_hash

    @property
    def coordinate_system(self) -> str:
        return self._coordinate_system

    @property
    def reference_name(self) -> str:
        return self._reference_name

    @property
    def biopython_version(self) -> str:
        return self._biopython_version

    @property
    def optimal_alignment_count(self):
        return self._optimal_alignment_count

    @property
    def alignment_is_ambiguous(self) -> bool:
        return self._alignment_is_ambiguous

    @property
    def identity_percent(self) -> float:
        denom = self.exact_matches + self.substitutions
        return (self.exact_matches / denom * 100.0) if denom > 0 else 0.0

    @property
    def study_coverage_percent(self) -> float:
        return (self.exact_matches + self.substitutions) / self.study_length * 100.0 if self.study_length > 0 else 0.0

    @property
    def reference_coverage_percent(self) -> float:
        return (self.exact_matches + self.substitutions) / self.reference_length * 100.0 if self.reference_length > 0 else 0.0

    @property
    def query_sequence_length(self) -> int:
        return self.study_length

    @property
    def reference_sequence_length(self) -> int:
        return self.reference_length

    @property
    def aligned_query_residues(self) -> int:
        return self.exact_matches + self.substitutions

    @property
    def mapped_atlas_positions(self) -> int:
        return self.exact_matches + self.substitutions

    @property
    def sequence_identity(self) -> float:
        denom = self.exact_matches + self.substitutions
        return (self.exact_matches / denom) if denom > 0 else 0.0

    @property
    def query_coverage(self) -> float:
        return (self.exact_matches + self.substitutions) / self.study_length if self.study_length > 0 else 0.0

    @property
    def reference_coverage(self) -> float:
        return (self.exact_matches + self.substitutions) / self.reference_length if self.reference_length > 0 else 0.0

    @property
    def number_of_insertions(self) -> int:
        return self.insertions

    @property
    def number_of_deletions(self) -> int:
        return self.deletions

    @property
    def number_of_unmapped_query_residues(self) -> int:
        return self.unmapped_residues

    @property
    def number_of_unmapped_atlas_positions(self) -> int:
        return self.reference_length - (self.exact_matches + self.substitutions)

    @property
    def mapping_quality_warnings(self) -> tuple[str, ...]:
        warns = []
        if self.query_coverage < 1.0:
            warns.append("incomplete query coverage")
        if self.reference_coverage < 1.0:
            warns.append("incomplete reference coverage")
        if self.number_of_insertions > 0:
            warns.append("insertions detected")
        if self.number_of_deletions > 0:
            warns.append("deletions detected")
        if self.number_of_unmapped_query_residues > 0:
            warns.append("mapping contains unmapped query residues")
        return tuple(warns)

    @property
    def warnings(self) -> tuple:
        return self._warnings

    def describe(self) -> str:
        """
        Returns a concise and factual textual description of the mapping result.
        """
        return (
            f"MappingResult for Study: {self.study_id} | "
            f"Reference: {self.reference_name} | "
            f"Identity: {self.identity_percent:.2f}% | "
            f"Coverage: {self.study_coverage_percent:.2f}% | "
            f"Score: {self.alignment_score} | "
            f"Warnings: {len(self.warnings)}"
        )

    def to_dict(self) -> dict:
        """
        Export the MappingResult object as a dictionary of native Python values.
        """
        return {
            "entity": "MappingResult",
            "schema_version": 1,
            "study_id": self.study_id,
            "coordinate_system": self.coordinate_system,
            "reference_name": self.reference_name,
            "biopython_version": self.biopython_version,
            "optimal_alignment_count": self.optimal_alignment_count,
            "alignment_is_ambiguous": self.alignment_is_ambiguous,
            "alignment_score": self.alignment_score,
            "exact_matches": self.exact_matches,
            "substitutions": self.substitutions,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "unmapped_residues": self.unmapped_residues,
            "study_length": self.study_length,
            "reference_length": self.reference_length,
            "alignment_length": self.alignment_length,
            "alignment_method": self.alignment_method,
            "scoring_parameters": self.scoring_parameters,
            "reference_sequence_hash": self.reference_sequence_hash,
            "identity_percent": self.identity_percent,
            "study_coverage_percent": self.study_coverage_percent,
            "reference_coverage_percent": self.reference_coverage_percent,
            "mapped_residues": [mr.to_dict() for mr in self.mapped_residues],
            "warnings": list(self.warnings),
            "query_sequence_length": self.query_sequence_length,
            "reference_sequence_length": self.reference_sequence_length,
            "aligned_query_residues": self.aligned_query_residues,
            "mapped_atlas_positions": self.mapped_atlas_positions,
            "sequence_identity": self.sequence_identity,
            "query_coverage": self.query_coverage,
            "reference_coverage": self.reference_coverage,
            "number_of_insertions": self.number_of_insertions,
            "number_of_deletions": self.number_of_deletions,
            "number_of_unmapped_query_residues": self.number_of_unmapped_query_residues,
            "number_of_unmapped_atlas_positions": self.number_of_unmapped_atlas_positions,
            "mapping_quality_warnings": list(self.mapping_quality_warnings),
        }

    def to_json(self) -> str:
        """
        Serializes the dictionary representation to a JSON string.
        """
        return json.dumps(self.to_dict(), sort_keys=True)
