from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ATLAS_DIR = PROJECT_ROOT / "atlas_v3"
FAMILIES_DIR = ATLAS_DIR / "families"

MASTER_TABLE = ATLAS_DIR / "atlas_v3_master_position_table.tsv"
EVOLUTIONARY_CANDIDATES = ATLAS_DIR / "evolutionary_candidates.tsv"
VALIDATED_CANDIDATES = ATLAS_DIR / "evolutionary_candidates_with_mutation_evidence.tsv"
KNOWN_MUTATIONS = ATLAS_DIR / "known_mutations_atlas_v3.tsv"

FAMILY_ASSIGNMENTS = FAMILIES_DIR / "petase_atlas_v3_family_assignments.tsv"
FAMILY_DEFINITIONS = FAMILIES_DIR / "family_definitions.tsv"
FAMILY_CONSENSUS_SUMMARY = FAMILIES_DIR / "family_consensus_summary.tsv"
FAMILY_VARIABILITY_INDEX = FAMILIES_DIR / "family_variability_index.tsv"
GLOBAL_FAMILY_CONSENSUS_MATRIX = FAMILIES_DIR / "global_family_consensus_matrix.tsv"
