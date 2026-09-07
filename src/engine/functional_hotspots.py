"""
Engine Module: Function-First PETase Hotspot Layer

Provides production Function-First WHERE Top30 position prioritization and
Evolutionary WHAT substitution proposals for PETase engineering.

Relying ONLY on:
- atlas_v3/functional_hotspot_reference.tsv (production reference resource)
- atlas_v3/atlas_v3_IsPETase_reference_table.tsv (master MSA counts table)

Strictly isolated from validation benchmark files.
Does NOT require FoldX or ESM at runtime.
"""

import os
import pandas as pd
from pathlib import Path

# Paths to production resources
PRODUCTION_REF_PATH = Path("atlas_v3/functional_hotspot_reference.tsv")
MASTER_TABLE_PATH = Path("atlas_v3/atlas_v3_IsPETase_reference_table.tsv")

CATALYTIC_TRIAD = {160, 206, 237}
DISULFIDE_CYSTEINES = {203, 239, 273, 289}
PROTECTED_POSITIONS = CATALYTIC_TRIAD.union(DISULFIDE_CYSTEINES)


class SubstitutionRecommendation:
    """Represents a single candidate substitution proposal."""

    def __init__(self, candidate_residue: str, evolutionary_rank: int, msa_count: int):
        self.candidate_residue = str(candidate_residue)
        self.evolutionary_rank = int(evolutionary_rank)
        self.msa_count = int(msa_count)

    def to_dict(self):
        return {
            "candidate_residue": self.candidate_residue,
            "evolutionary_rank": self.evolutionary_rank,
            "msa_count": self.msa_count
        }


class FunctionFirstPosition:
    """Represents one mapped Function-First Top30 candidate engineering position."""

    def __init__(
        self,
        where_rank: int,
        reference_position: int,
        reference_residue: str,
        query_position: int = None,
        query_residue: str = None,
        priority_group: str = "Group 8",
        functional_classes: str = "NONE",
        evolutionary_permissiveness: str = "LOW",
        is_protected: bool = False,
        substrate_distance: float = 99.0,
        catalytic_distance: float = 99.0,
        relative_sasa: float = 0.0,
        mapping_status: str = "EXACT_MATCH",
        substitutions: list = None,
        where_explanation: str = ""
    ):
        self.where_rank = int(where_rank)
        self.reference_position = int(reference_position)
        self.reference_residue = str(reference_residue)
        self.query_position = int(query_position) if query_position is not None else None
        self.query_residue = str(query_residue) if query_residue is not None else None
        self.priority_group = str(priority_group)
        self.functional_classes = str(functional_classes)
        self.evolutionary_permissiveness = str(evolutionary_permissiveness)
        self.is_protected = bool(is_protected)
        self.substrate_distance = float(substrate_distance)
        self.catalytic_distance = float(catalytic_distance)
        self.relative_sasa = float(relative_sasa)
        self.mapping_status = str(mapping_status)
        self.substitutions = substitutions if substitutions is not None else []
        self.where_explanation = str(where_explanation)

    @property
    def recommendation_status(self) -> str:
        if self.is_protected:
            return "EXCLUDED (PROTECTED CATALYTIC / DISULFIDE)"
        if self.query_position is None:
            return f"UNAVAILABLE ({self.mapping_status})"
        return "RECOMMENDED"

    def to_dict(self):
        return {
            "where_rank": self.where_rank,
            "query_position": self.query_position,
            "query_residue": self.query_residue,
            "reference_position": self.reference_position,
            "reference_residue": self.reference_residue,
            "priority_group": self.priority_group,
            "functional_classes": self.functional_classes,
            "evolutionary_permissiveness": self.evolutionary_permissiveness,
            "is_protected": self.is_protected,
            "recommendation_status": self.recommendation_status,
            "mapping_status": self.mapping_status,
            "substrate_distance": self.substrate_distance,
            "catalytic_distance": self.catalytic_distance,
            "relative_sasa": self.relative_sasa,
            "where_explanation": self.where_explanation,
            "substitutions": [s.to_dict() for s in self.substitutions]
        }


def parse_counts_string(counts_str):
    res_map = {}
    if pd.isna(counts_str) or not str(counts_str).strip():
        return res_map
    parts = str(counts_str).split(",")
    for p in parts:
        if ":" in p:
            aa, cnt = p.split(":")
            res_map[aa.strip()] = int(cnt.strip())
    return res_map


class FunctionFirstEngine:
    """Production Engine for Function-First WHERE Top30 prioritization & Evolutionary WHAT proposals."""

    def __init__(self, ref_path: Path = None, master_path: Path = None):
        ref_path = ref_path or PRODUCTION_REF_PATH
        master_path = master_path or MASTER_TABLE_PATH

        if not ref_path.exists():
            raise FileNotFoundError(f"Production reference table not found at: {ref_path}")
        if not master_path.exists():
            raise FileNotFoundError(f"Master table not found at: {master_path}")

        self.ref_df = pd.read_csv(ref_path, sep="\t")
        self.master_df = pd.read_csv(master_path, sep="\t")

        # Filter to pre-declared Top30
        self.top30_ref_df = self.ref_df[self.ref_df["in_top30"] == "YES"].sort_values(by="where_rank").reset_index(drop=True)

        # Parse MSA counts for all positions
        self.msa_counts_map = {}
        for _, r in self.master_df.iterrows():
            pos = int(r["IsPETase_position"])
            self.msa_counts_map[pos] = parse_counts_string(r["Counts"])

    def get_reference_top30(self) -> list:
        """Returns the frozen reference Top30 positions."""
        results = []
        for _, row in self.top30_ref_df.iterrows():
            pos = int(row["reference_position"])
            wt = str(row["wt_residue"])
            rk = int(row["where_rank"])
            is_prot = bool(row["is_protected"] == "YES") or (pos in PROTECTED_POSITIONS)

            # Evolutionary proposals for reference WT
            msa_counts = self.msa_counts_map.get(pos, {})
            non_wt = {aa: cnt for aa, cnt in msa_counts.items() if aa != wt}
            sorted_evo = sorted(non_wt.items(), key=lambda x: (-x[1], x[0]))

            proposals = []
            if not is_prot:
                for idx, (aa, cnt) in enumerate(sorted_evo[:5]):
                    proposals.append(SubstitutionRecommendation(candidate_residue=aa, evolutionary_rank=idx + 1, msa_count=cnt))

            explanation = f"Rank {rk} | Classes: {row['functional_classes']} | Permissiveness: {row['evolutionary_permissiveness']}"

            results.append(FunctionFirstPosition(
                where_rank=rk,
                reference_position=pos,
                reference_residue=wt,
                query_position=pos,
                query_residue=wt,
                priority_group=row["priority_group"],
                functional_classes=row["functional_classes"],
                evolutionary_permissiveness=row["evolutionary_permissiveness"],
                is_protected=is_prot,
                substrate_distance=float(row["substrate_distance"]),
                catalytic_distance=float(row["catalytic_distance"]),
                relative_sasa=float(row["relative_sasa"]),
                mapping_status="EXACT_MATCH",
                substitutions=proposals,
                where_explanation=explanation
            ))

        return results

    def project_top30_for_mapping(self, mapping_result) -> list:
        """Projects the Top30 Function-First shortlist onto a mapped query sequence."""
        # Create map from reference_position to MappedResidue or dict row
        ref_map = {}
        if hasattr(mapping_result, "mapped_residues"):
            for mr in mapping_result.mapped_residues:
                atlas_id = getattr(mr, "atlas_position_id", None)
                if atlas_id is not None:
                    ref_map[int(atlas_id)] = mr
        elif hasattr(mapping_result, "to_table"):
            for row in mapping_result.to_table():
                atlas_id = row.get("atlas_position_id")
                if atlas_id is not None:
                    ref_map[int(atlas_id)] = row

        results = []
        for _, row in self.top30_ref_df.iterrows():
            ref_pos = int(row["reference_position"])
            ref_wt = str(row["wt_residue"])
            rk = int(row["where_rank"])
            is_prot = bool(row["is_protected"] == "YES") or (ref_pos in PROTECTED_POSITIONS)

            mr = ref_map.get(ref_pos, None)

            if mr is not None:
                if isinstance(mr, dict):
                    q_pos = mr.get("study_position")
                    q_wt = mr.get("study_residue")
                    m_status = str(mr.get("mapping_status", "MAPPED"))
                else:
                    q_pos = getattr(mr, "study_position", None)
                    q_wt = getattr(mr, "study_residue", None)
                    m_status = mr.mapping_status.value if hasattr(mr.mapping_status, "value") else str(mr.mapping_status)
            else:
                q_pos = None
                q_wt = None
                m_status = "DELETED_IN_QUERY" if mr is not None else "UNMAPPED_IN_QUERY"

            # Evolutionary proposals for query WT
            proposals = []
            if not is_prot and q_wt is not None:
                msa_counts = self.msa_counts_map.get(ref_pos, {})
                # Ensure query WT is NOT recommended (query WT safety)
                non_q_wt = {aa: cnt for aa, cnt in msa_counts.items() if aa != q_wt}
                sorted_evo = sorted(non_q_wt.items(), key=lambda x: (-x[1], x[0]))

                for idx, (aa, cnt) in enumerate(sorted_evo[:5]):
                    proposals.append(SubstitutionRecommendation(candidate_residue=aa, evolutionary_rank=idx + 1, msa_count=cnt))

            explanation = f"Rank {rk} | Classes: {row['functional_classes']} | Permissiveness: {row['evolutionary_permissiveness']}"

            results.append(FunctionFirstPosition(
                where_rank=rk,
                reference_position=ref_pos,
                reference_residue=ref_wt,
                query_position=q_pos,
                query_residue=q_wt,
                priority_group=row["priority_group"],
                functional_classes=row["functional_classes"],
                evolutionary_permissiveness=row["evolutionary_permissiveness"],
                is_protected=is_prot,
                substrate_distance=float(row["substrate_distance"]),
                catalytic_distance=float(row["catalytic_distance"]),
                relative_sasa=float(row["relative_sasa"]),
                mapping_status=m_status,
                substitutions=proposals,
                where_explanation=explanation
            ))

        return results
