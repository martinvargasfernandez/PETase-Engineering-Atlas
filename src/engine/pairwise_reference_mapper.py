from engine.sequence_mapping_strategy import SequenceMappingStrategy
from engine.reference_mapper import ReferenceMapper
from engine.mapping_result import MappingResult

class PairwiseReferenceMapper(SequenceMappingStrategy):
    """
    Concrete pairwise alignment mapping strategy utilizing ReferenceMapper.
    """
    def __init__(self, coordinate_system: str = "IsPETase_v1"):
        self._mapper = ReferenceMapper(coordinate_system=coordinate_system)

    def map_sequence(self, study_sequence) -> MappingResult:
        return self._mapper.map_sequence(study_sequence)
