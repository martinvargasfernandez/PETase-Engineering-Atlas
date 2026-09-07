class SequenceAnalyzer:
    """
    Scientific Execution Engine: SequenceAnalyzer

    Orchestrates end-to-end sequence mapping, evidence projection, and family classification.
    Allows dependency injection for components.
    """

    def __init__(
        self,
        reference_mapper=None,
        evidence_projector=None,
        family_classifier=None
    ):
        from engine.reference_mapper import ReferenceMapper
        from engine.sequence_evidence_projector import SequenceEvidenceProjector
        from engine.family_classifier import FamilyClassifier

        self.reference_mapper = reference_mapper if reference_mapper is not None else ReferenceMapper()
        self.evidence_projector = evidence_projector if evidence_projector is not None else SequenceEvidenceProjector
        self.family_classifier = family_classifier if family_classifier is not None else FamilyClassifier()

    def analyze(self, study_sequence) -> "SequenceAnalysisResult":
        # Validate study_sequence interface via duck typing
        if not hasattr(study_sequence, "study_id") or not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")

        # 1. Coordinate Mapping
        mapping_result = self.reference_mapper.map_sequence(study_sequence)

        # 2. Evidence Projection
        if hasattr(self.evidence_projector, "project"):
            projected_sequence = self.evidence_projector.project(mapping_result)
        else:
            projected_sequence = self.evidence_projector(mapping_result)

        # 3. Family Classification
        family_classification = self.family_classifier.classify(projected_sequence)

        # 4. Integrate into Combined Result
        from engine.sequence_analysis_result import SequenceAnalysisResult
        return SequenceAnalysisResult(
            study_sequence=study_sequence,
            mapping_result=mapping_result,
            projected_sequence=projected_sequence,
            family_classification=family_classification
        )

    def analyze_sequence(
        self,
        raw_sequence: str,
        fasta_header: str = None,
        name: str = None,
        description: str = None,
        source: str = None,
        metadata: dict = None,
        study_id: str = None
    ) -> "SequenceAnalysisResult":
        from engine.study_sequence import StudySequence
        study_sequence = StudySequence(
            raw_sequence=raw_sequence,
            fasta_header=fasta_header,
            name=name,
            description=description,
            source=source,
            metadata=metadata,
            study_id=study_id
        )
        return self.analyze(study_sequence)

    def analyze_fasta(
        self,
        fasta_string: str,
        study_id: str = None
    ) -> "SequenceAnalysisResult":
        """
        Parses FASTA format string through StudySequence.from_fasta(),
        runs alignment, mapping, evidence projection, and family classification,
        and returns SequenceAnalysisResult.
        """
        from engine.study_sequence import StudySequence
        study_sequence = StudySequence.from_fasta(fasta_string, study_id=study_id)
        return self.analyze(study_sequence)
