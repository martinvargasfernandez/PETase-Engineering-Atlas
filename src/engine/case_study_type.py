from enum import Enum

class CaseStudyType(str, Enum):
    DOCKING = "docking"
    MOLECULAR_DYNAMICS = "molecular_dynamics"
    EXPERIMENTAL = "experimental"
    STRUCTURE = "structure"
    MUTATION_ANALYSIS = "mutation_analysis"
    OTHER = "other"
