import json

class ProjectedSequence:
    """
    Scientific Entity: ProjectedSequence

    Represents the complete projected MappingResult with all AtlasPosition evidence layers.
    Provides mapping summaries and native dict/json/table serializations.
    """

    def __init__(self, study_sequence, projected_residues: list, mapping_result):
        # Duck typing checks
        if not hasattr(study_sequence, "study_id") or not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")
        if not hasattr(mapping_result, "alignment_score") or not hasattr(mapping_result, "identity_percent"):
            raise TypeError("mapping_result must implement the MappingResult interface.")

        self._study_sequence = study_sequence
        self._projected_residues = tuple(projected_residues)
        self._mapping_result = mapping_result

        # 1. mapped_count: exact_matches + substitutions
        self._mapped_count = self._mapping_result.exact_matches + self._mapping_result.substitutions

        # 2. high_priority_count: projected records with an AtlasPosition and priority == "High"
        self._high_priority_count = sum(
            1 for pr in self._projected_residues 
            if pr.atlas_position_id is not None and pr.priority == "High"
        )

        # 3. positions_with_known_mutations: unique atlas_position_ids containing known mutations or mutation evidence
        unique_positions_with_mutations = set()
        for pr in self._projected_residues:
            if pr.atlas_position_id is not None:
                has_known = pr.known_mutations not in (None, "", "NA", "nan")
                
                # Check mutation evidence (typically "YES" vs "NO")
                has_evidence = False
                if pr.mutation_evidence is not None:
                    ev_str = str(pr.mutation_evidence).strip().upper()
                    if ev_str not in ("NO", "NA", "NAN", ""):
                        has_evidence = True
                
                if has_known or has_evidence:
                    unique_positions_with_mutations.add(pr.atlas_position_id)
        
        self._positions_with_known_mutations = len(unique_positions_with_mutations)

    @property
    def study_sequence(self):
        return self._study_sequence

    @property
    def study_id(self) -> str:
        return self._study_sequence.study_id

    @property
    def mapping_result(self):
        return self._mapping_result

    @property
    def projected_residues(self) -> tuple:
        return self._projected_residues

    @property
    def coordinate_system(self) -> str:
        return self._mapping_result.coordinate_system

    @property
    def identity_percent(self) -> float:
        return self._mapping_result.identity_percent

    @property
    def study_coverage_percent(self) -> float:
        return self._mapping_result.study_coverage_percent

    @property
    def reference_coverage_percent(self) -> float:
        return self._mapping_result.reference_coverage_percent

    @property
    def exact_matches(self) -> int:
        return self._mapping_result.exact_matches

    @property
    def substitutions(self) -> int:
        return self._mapping_result.substitutions

    @property
    def insertions(self) -> int:
        return self._mapping_result.insertions

    @property
    def deletions(self) -> int:
        return self._mapping_result.deletions

    @property
    def unmapped_residues(self) -> int:
        return self._mapping_result.unmapped_residues

    @property
    def mapped_count(self) -> int:
        return self._mapped_count

    @property
    def high_priority_count(self) -> int:
        return self._high_priority_count

    @property
    def positions_with_known_mutations(self) -> int:
        return self._positions_with_known_mutations

    @property
    def warnings(self) -> tuple:
        return self._mapping_result.warnings

    def describe(self) -> str:
        """
        Concise scientific summary description.
        """
        return (
            f"ProjectedSequence ID: {self.study_id} | "
            f"Mapped residues: {self.mapped_count}/{len(self.projected_residues)} | "
            f"High Priority residues: {self.high_priority_count} | "
            f"Known Mutations positions: {self.positions_with_known_mutations} | "
            f"Identity: {self.identity_percent:.2f}% | "
            f"Coverage: {self.study_coverage_percent:.2f}%"
        )

    def to_dict(self) -> dict:
        """
        Export the ProjectedSequence object as a dictionary of native Python values.
        """
        return {
            "entity": "ProjectedSequence",
            "schema_version": 1,
            "study_id": self.study_id,
            "coordinate_system": self.coordinate_system,
            "identity_percent": self.identity_percent,
            "study_coverage_percent": self.study_coverage_percent,
            "reference_coverage_percent": self.reference_coverage_percent,
            "exact_matches": self.exact_matches,
            "substitutions": self.substitutions,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "unmapped_residues": self.unmapped_residues,
            "mapped_count": self.mapped_count,
            "high_priority_count": self.high_priority_count,
            "positions_with_known_mutations": self.positions_with_known_mutations,
            "projected_residues": [pr.to_dict() for pr in self.projected_residues],
            "warnings": list(self.warnings),
        }

    def to_json(self) -> str:
        """
        Serializes the dictionary representation to a JSON string.
        """
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_table(self) -> list:
        """
        Returns a list of dictionaries with one row per projected mapping record,
        including deletion records.

        NOTE: This is a mapping/evidence table, representing the structural alignment
        columns, and does not strictly correspond 1-to-1 with physical study-sequence
        residues (as deletions have no physical study residue but are included here).
        """
        return [pr.to_dict() for pr in self.projected_residues]
