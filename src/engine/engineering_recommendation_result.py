import json
from typing import List, Dict, Any

class EngineeringRecommendationResult:
    """
    Structured outcome of the Project engineering analysis workflow,
    including a high-level metadata summary and position recommendations.
    """
    def __init__(
        self,
        project_id: str,
        study_id: str,
        predicted_family: str,
        family_classification_status: str,
        recommendations: List[Dict[str, Any]],
        positions_analyzed: List[int],
        active_case_studies_used: List[str],
        excluded_case_studies: List[str],
        warnings: List[str],
        analysis_method: str = "evidence_aware_recommender"
    ):
        self.project_id = str(project_id)
        self.study_id = str(study_id)
        self.predicted_family = str(predicted_family)
        self.family_classification_status = str(family_classification_status)
        self.recommendations = list(recommendations)
        self.positions_analyzed = list(positions_analyzed)
        self.active_case_studies_used = list(active_case_studies_used)
        self.excluded_case_studies = list(excluded_case_studies)
        self.warnings = list(warnings)
        self.analysis_method = str(analysis_method)
        self.analysis_version = "1.0"

        # Construct priority distribution
        priority_dist = {"High": 0, "Medium": 0, "Low": 0}
        for rec in self.recommendations:
            priority = rec.get("proposal_priority", "Low")
            priority_dist[priority] = priority_dist.get(priority, 0) + 1

        # Calculate evidence source count
        self.summary = {
            "project_id": self.project_id,
            "study_id": self.study_id,
            "predicted_family": self.predicted_family,
            "family_classification_status": self.family_classification_status,
            "positions_analyzed_count": len(self.positions_analyzed),
            "priority_distribution": priority_dist,
            "evidence_sources_count": len(self.active_case_studies_used),
            "active_case_studies_used": self.active_case_studies_used,
            "excluded_case_studies": self.excluded_case_studies,
            "warnings_count": len(self.warnings),
            "warnings": self.warnings,
            "analysis_method": self.analysis_method,
            "analysis_version": self.analysis_version
        }

    def describe(self) -> str:
        dist = self.summary["priority_distribution"]
        return (
            f"EngineeringRecommendationResult for Project {self.project_id} | "
            f"Analyzed: {len(self.positions_analyzed)} positions | "
            f"High Priority: {dist['High']} | "
            f"Medium Priority: {dist['Medium']} | "
            f"Low Priority: {dist['Low']} | "
            f"Case Studies: {len(self.active_case_studies_used)}"
        )

    def to_dict(self) -> dict:
        return {
            "entity": "EngineeringRecommendationResult",
            "schema_version": 1,
            "summary": self.summary,
            "recommendations": self.recommendations,
            "positions_analyzed": self.positions_analyzed,
            "active_case_studies_used": self.active_case_studies_used,
            "excluded_case_studies": self.excluded_case_studies,
            "warnings": self.warnings
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_table(self) -> List[Dict[str, Any]]:
        """
        Exposes a flat, clean array of dictionaries suitable for tabular display.
        """
        table = []
        for rec in self.recommendations:
            table.append({
                "atlas_position": rec["atlas_position"],
                "study_position": rec["study_position"],
                "wild_type": rec["wild_type"],
                "reference_residue": rec["reference_residue"],
                "proposed_mutant": rec["proposed_mutant"],
                "mutation": rec["mutation_label"],
                "score": rec["proposal_score"],
                "priority": rec["proposal_priority"],
                "atlas_score": rec["atlas_evidence_score"],
                "supporting_evidence": ", ".join(rec.get("supporting_evidence", [])),
                "contradictory_evidence": ", ".join(rec.get("contradictory_evidence", [])),
                "interpretation": rec.get("interpretation", ""),
                "evidence_explanation": rec["evidence_explanation"],
                "atlas_mutation_label": rec.get("atlas_mutation_label", rec["mutation_label"]),
                "project_mutation_label": rec.get("project_mutation_label"),
                "atlas_reference_residue": rec.get("atlas_reference_residue", rec["wild_type"]),
                "study_current_residue": rec.get("study_current_residue", "N/A"),
                "proposed_target_residue": rec.get("proposed_target_residue", rec["proposed_mutant"]),
                "mutation_actionability": rec.get("mutation_actionability", "unmapped")
            })
        return table
