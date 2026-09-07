from abc import ABC, abstractmethod
from engine.study_sequence import StudySequence
from engine.mapping_result import MappingResult

class SequenceMappingStrategy(ABC):
    """
    Abstract strategy defining the coordinate mapping interface.
    Allows dynamic substitution of alignment mapping algorithms.
    """
    @abstractmethod
    def map_sequence(self, study_sequence: StudySequence) -> MappingResult:
        """
        Maps a query study sequence to a reference coordinate template.
        """
        pass
