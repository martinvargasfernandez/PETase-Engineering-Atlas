import json
from engine.case_study_type import CaseStudyType
from engine.case_study_status import CaseStudyStatus

class PersistedCaseStudy:
    """
    Domain Entity: PersistedCaseStudy

    Represents a read-only persisted scientific case study linked to a Project.
    Provides immutable/defensive views of metadata, parameters, and evidence.
    """

    def __init__(
        self,
        case_study_id: str,
        project_id: str,
        study_id: str,
        study_type: CaseStudyType,
        title: str,
        description: str,
        created_at: str,
        updated_at: str,
        software: str,
        software_version: str,
        author: str,
        parameters: dict,
        input_files: list,
        result_files: list,
        residue_level_evidence: list,
        global_metrics: dict,
        warnings: list,
        provenance: dict,
        case_study_path: str,
        history: list,
        archived: bool = False,
        status: CaseStudyStatus = None,
        superseded_by_case_study_id: str = None,
        representative_structure = None
    ):
        self._case_study_id = str(case_study_id)
        self._project_id = str(project_id)
        self._study_id = str(study_id)
        self._study_type = CaseStudyType(study_type)
        self._title = str(title)
        self._description = str(description) if description is not None else ""
        self._created_at = str(created_at)
        self._updated_at = str(updated_at)
        self._software = str(software) if software is not None else ""
        self._software_version = str(software_version) if software_version is not None else ""
        self._author = str(author) if author is not None else ""
        self._parameters = dict(parameters) if parameters is not None else {}
        self._input_files = list(input_files) if input_files is not None else []
        self._result_files = list(result_files) if result_files is not None else []
        self._residue_level_evidence = list(residue_level_evidence) if residue_level_evidence is not None else []
        self._global_metrics = dict(global_metrics) if global_metrics is not None else {}
        self._warnings = list(warnings) if warnings is not None else []
        self._provenance = dict(provenance) if provenance is not None else {}
        self._case_study_path = str(case_study_path)
        self._history = list(history) if history is not None else []
        self._superseded_by_case_study_id = str(superseded_by_case_study_id) if superseded_by_case_study_id is not None else ""
        
        from engine.representative_structure import RepresentativeStructure
        if isinstance(representative_structure, dict):
            self._representative_structure = RepresentativeStructure.from_dict(representative_structure)
        else:
            self._representative_structure = representative_structure
        
        if status is not None:
            self._status = CaseStudyStatus(status)
        else:
            self._status = CaseStudyStatus.ARCHIVED if bool(archived) else CaseStudyStatus.ACTIVE

    @property
    def status(self) -> CaseStudyStatus:
        return self._status

    @property
    def superseded_by_case_study_id(self) -> str:
        return self._superseded_by_case_study_id

    @property
    def case_study_id(self) -> str:
        return self._case_study_id

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def study_id(self) -> str:
        return self._study_id

    @property
    def study_type(self) -> CaseStudyType:
        return self._study_type

    @property
    def title(self) -> str:
        return self._title

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
    def software(self) -> str:
        return self._software

    @property
    def software_version(self) -> str:
        return self._software_version

    @property
    def author(self) -> str:
        return self._author

    @property
    def parameters(self) -> dict:
        return dict(self._parameters)

    @property
    def input_files(self) -> list:
        return [dict(f) for f in self._input_files]

    @property
    def result_files(self) -> list:
        return [dict(f) for f in self._result_files]

    @property
    def residue_level_evidence(self) -> list:
        return [dict(e) for e in self._residue_level_evidence]

    @property
    def global_metrics(self) -> dict:
        return dict(self._global_metrics)

    @property
    def warnings(self) -> tuple:
        return tuple(self._warnings)

    @property
    def provenance(self) -> dict:
        return dict(self._provenance)

    @property
    def case_study_path(self) -> str:
        return self._case_study_path

    @property
    def history(self) -> list:
        return [dict(evt) for evt in self._history]

    @property
    def representative_structure(self):
        return self._representative_structure

    @property
    def archived(self) -> bool:
        return self.status == CaseStudyStatus.ARCHIVED

    def describe(self) -> str:
        return (
            f"CaseStudy: {self.title} ({self.case_study_id}) | "
            f"Type: {self.study_type.value} | "
            f"Project: {self.project_id} | "
            f"Sequence Reference: {self.study_id} | "
            f"Status: {self.status.value}"
        )

    def to_dict(self) -> dict:
        return {
            "entity": "PersistedCaseStudy",
            "schema_version": 1,
            "case_study_id": self.case_study_id,
            "project_id": self.project_id,
            "study_id": self.study_id,
            "study_type": self.study_type.value,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "software": self.software,
            "software_version": self.software_version,
            "author": self.author,
            "parameters": self.parameters,
            "input_files": self.input_files,
            "result_files": self.result_files,
            "residue_level_evidence": self.residue_level_evidence,
            "global_metrics": self.global_metrics,
            "warnings": list(self.warnings),
            "provenance": self.provenance,
            "case_study_path": self.case_study_path,
            "history": self.history,
            "archived": self.archived,
            "status": self.status.value,
            "superseded_by_case_study_id": self.superseded_by_case_study_id,
            "representative_structure": self.representative_structure.to_dict() if self.representative_structure is not None else None
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
