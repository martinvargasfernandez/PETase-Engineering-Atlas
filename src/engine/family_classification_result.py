import json

class FamilyClassificationResult:
    """
    Scientific Entity: FamilyClassificationResult

    Represents the output of the FamilyClassifier containing ranked scores,
    classification statuses, margins, and the list of most informative supporting residues.
    """

    def __init__(
        self,
        study_id: str,
        predicted_family: str,
        classification_status: str,
        confidence_status: str,
        ranked_family_scores: list,
        best_score: float,
        second_best_score: float,
        score_margin: float,
        mapped_positions_used: int,
        informative_positions_used: int,
        missing_positions: int,
        warnings: list,
        informative_residues: list,
        method: str = "weighted_consensus_agreement",
        method_version: str = "1.0"
    ):
        self._study_id = str(study_id)
        self._predicted_family = str(predicted_family)
        
        valid_statuses = {"classified", "ambiguous", "insufficient_evidence", "unclassified"}
        if classification_status not in valid_statuses:
            raise ValueError(f"Invalid classification_status '{classification_status}'.")
        self._classification_status = classification_status

        valid_confidences = {"high", "medium", "low"}
        if confidence_status not in valid_confidences:
            raise ValueError(f"Invalid confidence_status '{confidence_status}'.")
        self._confidence_status = confidence_status

        self._ranked_family_scores = list(ranked_family_scores)
        self._best_score = float(best_score)
        self._second_best_score = float(second_best_score)
        self._score_margin = float(score_margin)
        self._mapped_positions_used = int(mapped_positions_used)
        self._informative_positions_used = int(informative_positions_used)
        self._missing_positions = int(missing_positions)
        self._warnings = tuple(warnings) if warnings is not None else ()
        self._informative_residues = list(informative_residues)
        self._method = str(method)
        self._method_version = str(method_version)

    @property
    def study_id(self) -> str:
        return self._study_id

    @property
    def predicted_family(self) -> str:
        return self._predicted_family

    @property
    def classification_status(self) -> str:
        return self._classification_status

    @property
    def confidence_status(self) -> str:
        return self._confidence_status

    @property
    def ranked_family_scores(self) -> list:
        return list(self._ranked_family_scores)

    @property
    def best_score(self) -> float:
        return self._best_score

    @property
    def second_best_score(self) -> float:
        return self._second_best_score

    @property
    def score_margin(self) -> float:
        return self._score_margin

    @property
    def mapped_positions_used(self) -> int:
        return self._mapped_positions_used

    @property
    def informative_positions_used(self) -> int:
        return self._informative_positions_used

    @property
    def missing_positions(self) -> int:
        return self._missing_positions

    @property
    def warnings(self) -> tuple:
        return self._warnings

    @property
    def informative_residues(self) -> list:
        return list(self._informative_residues)

    @property
    def method(self) -> str:
        return self._method

    @property
    def method_version(self) -> str:
        return self._method_version

    def describe(self) -> str:
        """
        Concise scientific summary description.
        """
        return (
            f"FamilyClassificationResult for {self.study_id} | "
            f"Predicted Family: {self.predicted_family} | "
            f"Status: {self.classification_status} | "
            f"Confidence: {self.confidence_status} | "
            f"Score: {self.best_score:.4f} | "
            f"Margin: {self.score_margin:.4f} | "
            f"Informative Residues: {len(self.informative_residues)}"
        )

    def to_dict(self) -> dict:
        """
        Export as dictionary format.
        """
        return {
            "entity": "FamilyClassificationResult",
            "schema_version": 1,
            "study_id": self.study_id,
            "predicted_family": self.predicted_family,
            "classification_status": self.classification_status,
            "confidence_status": self.confidence_status,
            "ranked_family_scores": self.ranked_family_scores,
            "best_score": self.best_score,
            "second_best_score": self.second_best_score,
            "score_margin": self.score_margin,
            "mapped_positions_used": self.mapped_positions_used,
            "informative_positions_used": self.informative_positions_used,
            "missing_positions": self.missing_positions,
            "warnings": list(self.warnings),
            "informative_residues": self.informative_residues,
            "method": self.method,
            "method_version": self.method_version
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)
