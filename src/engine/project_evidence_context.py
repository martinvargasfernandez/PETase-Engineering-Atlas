import json
from typing import List, Dict, Any
from engine.project import Project
from engine.case_study_status import CaseStudyStatus
from engine.case_study_repository import CaseStudyRepository

class ResidueEvidence:
    """
    Typed scientific representation of an evidence record at a specific residue position.
    """
    def __init__(self, raw_data: dict, atlas_position_id: int = None):
        self.position = int(raw_data.get("position")) if raw_data.get("position") is not None else None
        self.atlas_position_id = atlas_position_id
        
        # Determine the evidence type based on parsed keys or method provenance
        self.evidence_type = raw_data.get("evidence_type") or raw_data.get("type")
        if not self.evidence_type:
            mt = raw_data.get("metric_type", "")
            if mt == "rmsf":
                self.evidence_type = "simulation_rmsf"
            elif mt == "contact_frequency":
                self.evidence_type = "simulation_contact"
            elif mt == "hbond_persistence":
                self.evidence_type = "simulation_hbond"
            elif mt == "interaction_energy":
                self.evidence_type = "simulation_energy"
            else:
                method = raw_data.get("method", "").lower()
                if "rmsf" in method or "rmsf" in raw_data:
                    self.evidence_type = "simulation_rmsf"
                elif "contact" in method or "contact" in raw_data or "frequency" in raw_data:
                    self.evidence_type = "simulation_contact"
                elif "hbond" in method or "hbond" in raw_data or "donor" in raw_data or "acceptor" in raw_data:
                    self.evidence_type = "simulation_hbond"
                elif "energy" in method or "energy" in raw_data or "coul_sr" in raw_data or "lj_sr" in raw_data:
                    self.evidence_type = "simulation_energy"
                elif "dock" in method or "docking" in raw_data:
                    self.evidence_type = "structural_docking"
                elif "experimental" in method or "experimental" in raw_data:
                    self.evidence_type = "experimental_activity"
                else:
                    self.evidence_type = "unknown"

        # Extract values
        self.value = raw_data.get("value")
        if self.value is None:
            # Fallback to key-based extraction if value is not nested
            if "rmsf" in raw_data:
                self.value = raw_data["rmsf"]
            elif "frequency" in raw_data:
                self.value = raw_data["frequency"]
            elif "persistence" in raw_data:
                self.value = raw_data["persistence"]
            elif "total_energy" in raw_data:
                self.value = raw_data["total_energy"]
            elif "energy_total" in raw_data:
                self.value = raw_data["energy_total"]
            else:
                self.value = raw_data

        self.simulation_id = raw_data.get("simulation_id", "")
        self.update_id = raw_data.get("update_id", "")
        self.created_at = raw_data.get("created_at", "")
        self.source = raw_data.get("source", "")
        self.method = raw_data.get("method", "")
        self.method_version = raw_data.get("method_version", "")
        self.units = raw_data.get("units")
        self.raw_data = dict(raw_data)

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "atlas_position_id": self.atlas_position_id,
            "evidence_type": self.evidence_type,
            "value": self.value,
            "simulation_id": self.simulation_id,
            "update_id": self.update_id,
            "created_at": self.created_at,
            "source": self.source,
            "method": self.method,
            "method_version": self.method_version,
            "units": self.units,
            "raw_data": self.raw_data
        }

class ProjectEvidenceContext:
    """
    Read-only entity aggregating project-specific CaseStudy evidence,
    coordinate mappings, and warnings.
    """
    def __init__(self, project: Project, statuses: List[CaseStudyStatus] = None):
        self.project_id = project.project_id
        self.study_id = project.primary_study_sequence.study_id
        self.reference_context_id = project.primary_study_sequence.study_id
        self.reference_context_sequence = project.primary_study_sequence.raw_sequence
        
        # Extract family classification from sequence analysis result (supports both runtime and persisted formats)
        sar = project.sequence_analysis_result
        if hasattr(sar, "family_classification") and sar.family_classification is not None:
            self.predicted_family = sar.family_classification.predicted_family
            self.family_classification_status = sar.family_classification.classification_status
        elif hasattr(sar, "family_classification_summary") and sar.family_classification_summary is not None:
            self.predicted_family = sar.family_classification_summary.get("predicted_family", "")
            self.family_classification_status = sar.family_classification_summary.get("classification_status", "")
        else:
            self.predicted_family = ""
            self.family_classification_status = ""
        
        # Build sequence coordinate mappings from residue table
        self._study_to_atlas = {}
        self._atlas_to_study = {}
        for row in sar.to_table():
            study_pos = row.get("study_position")
            atlas_id = row.get("atlas_position_id")
            is_mapped = row.get("is_mapped", False)
            
            if study_pos is not None and is_mapped and atlas_id is not None:
                self._study_to_atlas[study_pos] = atlas_id
                self._atlas_to_study[atlas_id] = study_pos

        # Determine target statuses
        if statuses is None:
            statuses = [CaseStudyStatus.ACTIVE]
        else:
            statuses = [CaseStudyStatus(s) for s in statuses]

        # Load project case studies
        cs_repo = CaseStudyRepository()
        summaries = cs_repo.list_case_studies(project, include_archived=True)
        
        self.active_case_studies = []
        self.superseded_case_studies = []
        self.warnings = []
        self.global_metrics = {}
        self.provenance = {
            "source": "ProjectEvidenceContext",
            "schema_version": 1
        }
        
        excluded_statuses = []
        for summ in summaries:
            cs = cs_repo.load_case_study(project, summ["case_study_id"])
            if cs.status in statuses:
                if cs.status == CaseStudyStatus.ACTIVE:
                    self.active_case_studies.append(cs)
                elif cs.status == CaseStudyStatus.SUPERSEDED:
                    self.superseded_case_studies.append(cs)
            else:
                excluded_statuses.append(cs.status.value)

        # Process and align residue evidence
        self.residue_evidence_by_study_position = {}
        self.residue_evidence_by_atlas_position = {}

        # Parse evidence from chosen case studies
        all_studies = self.active_case_studies + self.superseded_case_studies
        for cs in all_studies:
            # Aggregate global metrics
            for metric_key, metric_record in cs.global_metrics.items():
                self.global_metrics.setdefault(metric_key, []).append(metric_record)

            # Process residue-level evidence
            for ev_dict in cs.residue_level_evidence:
                study_pos = ev_dict.get("position")
                if study_pos is None:
                    continue
                
                # Check mapping
                atlas_pos_id = self._study_to_atlas.get(study_pos)
                typed_ev = ResidueEvidence(ev_dict, atlas_position_id=atlas_pos_id)
                
                # Exclude superseded case studies from the active mapping context
                if cs.status == CaseStudyStatus.ACTIVE:
                    self.residue_evidence_by_study_position.setdefault(study_pos, []).append(typed_ev)
                    if atlas_pos_id is not None:
                        self.residue_evidence_by_atlas_position.setdefault(atlas_pos_id, []).append(typed_ev)
                    else:
                        self.warnings.append(
                            f"Evidence of type '{typed_ev.evidence_type}' at study position {study_pos} "
                            f"in CaseStudy '{cs.case_study_id}' has no corresponding Atlas coordinate mapping."
                        )

    def describe(self) -> str:
        return (
            f"ProjectEvidenceContext for {self.project_id} ({self.study_id}) | "
            f"Predicted Family: {self.predicted_family} | "
            f"Active Case Studies: {len(self.active_case_studies)} | "
            f"Warnings: {len(self.warnings)}"
        )

    def to_dict(self) -> dict:
        return {
            "entity": "ProjectEvidenceContext",
            "project_id": self.project_id,
            "study_id": self.study_id,
            "reference_context_id": self.reference_context_id,
            "reference_context_sequence": self.reference_context_sequence,
            "predicted_family": self.predicted_family,
            "family_classification_status": self.family_classification_status,
            "active_case_studies": [cs.to_dict() for cs in self.active_case_studies],
            "superseded_case_studies": [cs.to_dict() for cs in self.superseded_case_studies],
            "residue_evidence_by_study_position": {
                pos: [e.to_dict() for e in evs]
                for pos, evs in self.residue_evidence_by_study_position.items()
            },
            "residue_evidence_by_atlas_position": {
                pos: [e.to_dict() for e in evs]
                for pos, evs in self.residue_evidence_by_atlas_position.items()
            },
            "global_metrics": self.global_metrics,
            "warnings": self.warnings,
            "provenance": self.provenance
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
