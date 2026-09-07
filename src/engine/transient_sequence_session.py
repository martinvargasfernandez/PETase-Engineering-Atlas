class TransientSequenceSession:
    """
    Transient value object representing a custom sequence analysis session.
    Encapsulates all mapping results, projected evidence, and recommendations.
    """
    def __init__(
        self,
        study_sequence,
        mapping_result,
        projected_sequence,
        family_classification,
        recommendations: list,
        atlas_coordinate_system: str = "IsPETase_v1",
        function_first_hotspots: list = None
    ):
        self.study_sequence = study_sequence
        self.mapping_result = mapping_result
        self.projected_sequence = projected_sequence
        self.family_classification = family_classification
        self.recommendations = recommendations
        self.atlas_coordinate_system = str(atlas_coordinate_system)
        self.function_first_hotspots = function_first_hotspots if function_first_hotspots is not None else []

    def to_dict(self) -> dict:
        """
        Serializes the session state to a dictionary for UI presentation.
        """
        return {
            "study_sequence": self.study_sequence.to_dict() if hasattr(self.study_sequence, "to_dict") else str(self.study_sequence),
            "mapping_result": self.mapping_result.to_dict() if hasattr(self.mapping_result, "to_dict") else {},
            "projected_sequence": self.projected_sequence.to_dict() if hasattr(self.projected_sequence, "to_dict") else {},
            "family_classification": self.family_classification.to_dict() if hasattr(self.family_classification, "to_dict") else {},
            "recommendations": self.recommendations,
            "function_first_hotspots": [h.to_dict() if hasattr(h, "to_dict") else h for h in self.function_first_hotspots],
            "atlas_coordinate_system": self.atlas_coordinate_system
        }
