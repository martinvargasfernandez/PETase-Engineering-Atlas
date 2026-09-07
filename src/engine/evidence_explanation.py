from typing import List, Dict, Any

class EvidenceExplanation:
    """
    Scientific Value Object representing the traceable rationale
    behind an engineering recommendation.
    """
    def __init__(
        self,
        supporting_evidence: List[str],
        contradictory_evidence: List[str],
        missing_evidence: List[str],
        final_interpretation: str
    ):
        self.supporting_evidence = list(supporting_evidence)
        self.contradictory_evidence = list(contradictory_evidence)
        self.missing_evidence = list(missing_evidence)
        self.final_interpretation = final_interpretation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "missing_evidence": self.missing_evidence,
            "final_interpretation": self.final_interpretation
        }
