from engine.sequence_mapping_strategy import SequenceMappingStrategy

class FutureProfileMapper(SequenceMappingStrategy):
    """
    Placeholder profile alignment mapper strategy (for future profile/HMM capabilities).
    """
    def map_sequence(self, study_sequence):
        raise NotImplementedError("Profile-based HMM alignment mapping is not implemented in V1.")
