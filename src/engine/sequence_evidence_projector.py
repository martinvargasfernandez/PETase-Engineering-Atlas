from engine.projected_residue import ProjectedResidue
from engine.projected_sequence import ProjectedSequence

class SequenceEvidenceProjector:
    """
    Scientific Execution Engine: SequenceEvidenceProjector

    Consumes a MappingResult and projects AtlasPosition evidence onto mapped study residues,
    preserving global and family evidence as distinct layers.
    Does not run alignments, family classifications, or database queries.
    """

    @staticmethod
    def project(mapping_result) -> ProjectedSequence:
        # Duck typing validation for MappingResult
        if not hasattr(mapping_result, "study_sequence") or not hasattr(mapping_result, "mapped_residues"):
            raise TypeError("mapping_result must implement the MappingResult interface.")

        projected_residues = []
        for mr in mapping_result.mapped_residues:
            pr = ProjectedResidue(mr)
            projected_residues.append(pr)

        return ProjectedSequence(
            study_sequence=mapping_result.study_sequence,
            projected_residues=projected_residues,
            mapping_result=mapping_result
        )
