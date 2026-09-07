import json

class Project:
    """
    Domain Entity: Project

    Exposes read-only access to persistent project details, including the primary sequence,
    persisted analysis view, and historic scientific milestones.
    """

    def __init__(
        self,
        project_id: str,
        project_name: str,
        description: str,
        created_at: str,
        updated_at: str,
        project_path: str,
        primary_study_sequence,
        sequence_analysis_result,
        atlas_version: str,
        coordinate_system: str,
        analysis_version: str,
        project_status: list,
        history: list,
        warnings: list = None
    ):
        self._project_id = str(project_id)
        self._project_name = str(project_name)
        self._description = str(description) if description is not None else ""
        self._created_at = str(created_at)
        self._updated_at = str(updated_at)
        self._project_path = str(project_path)
        self._primary_study_sequence = primary_study_sequence
        self._sequence_analysis_result = sequence_analysis_result
        self._atlas_version = str(atlas_version)
        self._coordinate_system = str(coordinate_system)
        self._analysis_version = str(analysis_version)
        self._project_status = list(project_status)
        self._history = list(history)
        self._warnings = tuple(warnings) if warnings is not None else ()

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def description(self) -> str:
        return self._description

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def updated_at(self) -> str:
        return self._updated_at

    @property
    def project_path(self) -> str:
        return self._project_path

    @property
    def primary_study_sequence(self):
        return self._primary_study_sequence

    @property
    def sequence_analysis_result(self):
        return self._sequence_analysis_result

    @property
    def atlas_version(self) -> str:
        return self._atlas_version

    @property
    def coordinate_system(self) -> str:
        return self._coordinate_system

    @property
    def analysis_version(self) -> str:
        return self._analysis_version

    @property
    def classification_method(self) -> str:
        if self._sequence_analysis_result is not None:
            return self._sequence_analysis_result.classification_method
        return "FamilyClassifier_v1"

    @property
    def project_status(self) -> list:
        return list(self._project_status)

    @property
    def history(self) -> list:
        return list(self._history)

    @property
    def warnings(self) -> tuple:
        return self._warnings

    def describe(self) -> str:
        return (
            f"Project: {self.project_name} ({self.project_id}) | "
            f"Status: {', '.join(self.project_status)} | "
            f"Coordinate System: {self.coordinate_system} | "
            f"Atlas Version: {self.atlas_version} | "
            f"History Events: {len(self.history)}"
        )

    def to_dict(self) -> dict:
        return {
            "entity": "Project",
            "schema_version": 1,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "project_path": self.project_path,
            "atlas_version": self.atlas_version,
            "coordinate_system": self.coordinate_system,
            "analysis_version": self.analysis_version,
            "classification_method": self.classification_method,
            "project_status": self.project_status,
            "history": self.history,
            "warnings": list(self.warnings),
            "primary_study_sequence": self.primary_study_sequence.to_dict() if self.primary_study_sequence is not None else None,
            "sequence_analysis_result": self.sequence_analysis_result.to_dict(include_residue_table=False) if self.sequence_analysis_result is not None else None
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)


class PersistedSequenceAnalysisResult:
    """
    Exposes only data actually persisted from the SequenceAnalysisResult JSON,
    without database lookups or rerunning mapping logic.
    """

    def __init__(self, analysis_data: dict, residue_table: list):
        self._analysis_data = dict(analysis_data)
        self._residue_table = list(residue_table)

    @property
    def study_id(self) -> str:
        return self._analysis_data.get("study_id", "")

    @property
    def coordinate_system(self) -> str:
        return self._analysis_data.get("coordinate_system", "")

    @property
    def sequence_hash(self) -> str:
        return self._analysis_data.get("sequence_hash", "")

    @property
    def analysis_method(self) -> str:
        return self._analysis_data.get("analysis_method", "")

    @property
    def analysis_version(self) -> str:
        return self._analysis_data.get("analysis_version", "")

    @property
    def classification_method(self) -> str:
        return self._analysis_data.get("classification_method", "FamilyClassifier_v1")

    @property
    def mapping_summary(self) -> dict:
        return dict(self._analysis_data.get("mapping", {}))

    @property
    def family_classification_summary(self) -> dict:
        return dict(self._analysis_data.get("family_classification", {}))

    @property
    def warnings(self) -> tuple:
        raw_warnings = self._analysis_data.get("warnings", [])
        return tuple(raw_warnings)

    @property
    def residue_table(self) -> list:
        return list(self._residue_table)

    def describe(self) -> str:
        mapping = self.mapping_summary
        fam = self.family_classification_summary
        return (
            f"PersistedSequenceAnalysisResult for {self.study_id} | "
            f"Predicted Family: {fam.get('predicted_family')} | "
            f"Identity: {mapping.get('identity_percent', 0.0):.2f}% | "
            f"Warnings: {len(self.warnings)}"
        )

    def to_table(self) -> list:
        return list(self._residue_table)

    def to_dict(self, include_residue_table: bool = False) -> dict:
        data = dict(self._analysis_data)
        if include_residue_table:
            data["residue_table"] = list(self._residue_table)
        else:
            data.pop("residue_table", None)
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(include_residue_table=False), sort_keys=True)
