import json
import uuid
import datetime

class CaseStudyUpdate:
    """
    Update Payload Entity: CaseStudyUpdate

    Represents a read-only structured payload containing additive evidence, metrics,
    references, and update-level provenance.
    """

    def __init__(
        self,
        source: str,
        method: str,
        method_version: str,
        residue_level_evidence: list = None,
        global_metrics: dict = None,
        result_files: list = None,
        warnings: list = None,
        provenance: dict = None,
        notes: list = None,
        update_id: str = None,
        created_at: str = None,
        representative_structure_request: dict = None
    ):
        self._source = str(source)
        self._method = str(method)
        self._method_version = str(method_version)
        
        self._residue_level_evidence = list(residue_level_evidence) if residue_level_evidence is not None else []
        self._global_metrics = dict(global_metrics) if global_metrics is not None else {}
        self._result_files = list(result_files) if result_files is not None else []
        self._warnings = list(warnings) if warnings is not None else []
        self._provenance = dict(provenance) if provenance is not None else {}
        self._notes = list(notes) if notes is not None else []
        self._representative_structure_request = dict(representative_structure_request) if representative_structure_request is not None else None
 
        # Validate that at least one additive field is non-empty
        if not (self._residue_level_evidence or self._global_metrics or self._result_files or self._warnings or self._provenance or self._notes or self._representative_structure_request):
            raise ValueError("CaseStudyUpdate must contain at least one non-empty update field.")

        if update_id is not None:
            try:
                uuid.UUID(str(update_id))
                self._update_id = str(update_id)
            except ValueError:
                raise ValueError(f"Invalid update_id UUID: {update_id}")
        else:
            self._update_id = str(uuid.uuid4())

        self._created_at = str(created_at) if created_at is not None else datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Prevent large inline binary payloads (1MB maximum)
        try:
            if len(self.to_json()) > 1024 * 1024:
                raise ValueError("Payload size exceeds maximum allowed size (1MB).")
        except (TypeError, ValueError):
            pass

    @property
    def update_id(self) -> str:
        return self._update_id

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def source(self) -> str:
        return self._source

    @property
    def method(self) -> str:
        return self._method

    @property
    def method_version(self) -> str:
        return self._method_version

    @property
    def residue_level_evidence(self) -> list:
        return [dict(e) for e in self._residue_level_evidence]

    @property
    def global_metrics(self) -> dict:
        return dict(self._global_metrics)

    @property
    def result_files(self) -> list:
        return [dict(f) for f in self._result_files]

    @property
    def warnings(self) -> tuple:
        return tuple(self._warnings)

    @property
    def provenance(self) -> dict:
        return dict(self._provenance)

    @property
    def notes(self) -> list:
        return list(self._notes)

    @property
    def representative_structure_request(self) -> dict:
        return dict(self._representative_structure_request) if self._representative_structure_request is not None else None

    def describe(self) -> str:
        return (
            f"CaseStudyUpdate {self.update_id} | Source: {self.source} | "
            f"Method: {self.method} ({self.method_version}) | "
            f"Evidence Count: {len(self.residue_level_evidence)}"
        )

    def to_dict(self) -> dict:
        return {
            "entity": "CaseStudyUpdate",
            "update_id": self.update_id,
            "created_at": self.created_at,
            "source": self.source,
            "method": self.method,
            "method_version": self.method_version,
            "residue_level_evidence": self.residue_level_evidence,
            "global_metrics": self.global_metrics,
            "result_files": self.result_files,
            "warnings": list(self.warnings),
            "provenance": self.provenance,
            "notes": self.notes,
            "representative_structure_request": self.representative_structure_request
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
