from enum import Enum

class MappingStatus(Enum):
    """
    MappingStatus Enum representing the alignment state of a mapped residue.
    """
    EXACT_MATCH = "exact_match"
    SUBSTITUTION = "substitution"
    INSERTION = "insertion"
    DELETION = "deletion"
    UNMAPPED = "unmapped"
