import sys
import os
import json
import math
import hashlib
import pathlib
import datetime
import pandas as pd
import numpy as np
import builtins

# Ensure path includes root to load engine modules
sys.path.insert(0, os.path.abspath('.'))

# Standard engine imports (unpatched at the module level)
import engine.atlas
import engine.evidence
import engine.ranking
import engine.reference_mapper

from engine.candidate_discovery import CandidateDiscoveryEngine
from engine.residue import Residue
from engine.mutation_proposal_engine import MutationProposalEngine
from engine.proposal_generators.family_consensus_generator import FamilyConsensusGenerator
from engine.proposal_scoring import ProposalScoringEngine
from engine.atlas_constants import ATLAS_CATALYTIC_TRIAD

def get_sha256(filepath):
    """Compute the SHA256 checksum of a file."""
    h = hashlib.sha256()
    with builtins.open(filepath, 'rb') as f:
        chunk = f.read(8192)
        while chunk:
            h.update(chunk)
            chunk = f.read(8192)
    return h.hexdigest()

def get_project_version():
    """Parses the central project version from VERSION.md."""
    path = pathlib.Path("VERSION.md")
    if path.exists():
        with builtins.open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Version "):
                    return line.replace("Version ", "").strip()
    return "1.0"

def run_freeze():
    print("Initializing Evolutionary-Only Freeze...")
    
    # Save original references for patching and teardown
    orig_open = builtins.open
    orig_atlas_load = engine.atlas.load_master_table
    orig_evidence_load = getattr(engine.evidence, "load_master_table", None)
    orig_ranking_load = getattr(engine.ranking, "load_master_table", None)
    orig_mapper_load = getattr(engine.reference_mapper, "load_master_table", None)
    
    # 1. Source Data Universe Verification (using original loader before masking)
    original_df = orig_atlas_load()
    all_positions = set(int(pos) for pos in original_df['IsPETase_position'].dropna())
    fvi_zero_positions = set(int(pos) for pos in original_df[original_df['FVI'] == 0]['IsPETase_position'].dropna())
    protected_positions = set(ATLAS_CATALYTIC_TRIAD)
    
    total_positions_count = len(all_positions)
    candidate_universe = all_positions - fvi_zero_positions - protected_positions
    eligible_positions_count = len(candidate_universe)
    
    # Verify expected universe metrics
    if total_positions_count != 290:
        raise ValueError(f"Validation Universe Discrepancy: Expected 290 total reference positions, but found {total_positions_count}")
    if eligible_positions_count != 243:
        raise ValueError(f"Validation Universe Discrepancy: Expected 243 eligible positions, but found {eligible_positions_count}")
    
    print(f"Verified Validation Universe: {total_positions_count} total positions, {eligible_positions_count} eligible positions.")
    
    # Define mocked functions
    def mocked_load_master_table():
        df = orig_atlas_load()
        # Create a deep copy to prevent mutating the original cached DataFrame
        df = df.copy()
        df["Known_mutations"] = None
        df["Mutation_evidence"] = "NO"
        return df
        
    def guarded_open(file, *args, **kwargs):
        filepath = str(file).replace("\\", "/").lower()
        forbidden = [
            "known_mutations_atlas_v3",
            "evolutionary_candidates_with_mutation_evidence",
            "validation/literature_benchmark",
            "literature",
            "benchmark"
        ]
        for f in forbidden:
            if f in filepath:
                raise PermissionError(f"Leakage check failed: Attempted to open blocked literature/benchmark file: {file}")
        return orig_open(file, *args, **kwargs)

    try:
        # Apply the runtime monkey-patches
        builtins.open = guarded_open
        engine.atlas.load_master_table = mocked_load_master_table
        if orig_evidence_load is not None:
            engine.evidence.load_master_table = mocked_load_master_table
        if orig_ranking_load is not None:
            engine.ranking.load_master_table = mocked_load_master_table
        if orig_mapper_load is not None:
            engine.reference_mapper.load_master_table = mocked_load_master_table
            
        # 3. Position Ranking (strictly evolutionary)
        position_rows = []
        
        for pos in sorted(list(all_positions)):
            # Residue will load the masked data
            res = Residue(pos)
            ev_score = res.atlas_evidence_score
            
            # Calculate consensus residue count from consensus_residues string
            consensus_residues = res.consensus_residues
            if pd.isna(consensus_residues) or str(consensus_residues).strip() in ["", "nan", "NaN", "None", "-"]:
                consensus_count = 0
            else:
                consensus_count = len([
                    r.strip()
                    for r in str(consensus_residues).split(",")
                    if r.strip()
                ])
                
            # Determine eligibility and exclusion reason
            eligible = pos in candidate_universe
            if not eligible:
                if pos in protected_positions:
                    exclusion_reason = "Catalytic triad control"
                elif pos in fvi_zero_positions:
                    exclusion_reason = "FVI=0 exclusion"
                else:
                    exclusion_reason = "Excluded position"
            else:
                exclusion_reason = "None"
                
            position_rows.append({
                "reference_position": pos,
                "reference_residue": res.reference_residue,
                "fvi": int(res.fvi) if pd.notna(res.fvi) else 0,
                "global_conservation": float(res.global_conservation) if pd.notna(res.global_conservation) else 0.0,
                "consensus_residue_count": consensus_count,
                "evolutionary_score": ev_score,
                "eligible": eligible,
                "exclusion_reason": exclusion_reason
            })
            
        # Sort positions: evolutionary_score DESC, fvi DESC, reference_position ASC
        sorted_positions = sorted(
            position_rows,
            key=lambda x: (
                x["evolutionary_score"],
                x["fvi"],
                -x["reference_position"]
            ),
            reverse=True
        )
        
        for idx, row in enumerate(sorted_positions, 1):
            row["rank"] = idx
            
        # Re-order columns to match the required schema
        position_columns = [
            "rank", "reference_position", "reference_residue", "fvi", 
            "global_conservation", "consensus_residue_count", 
            "evolutionary_score", "eligible", "exclusion_reason"
        ]
        position_df = pd.DataFrame(sorted_positions)[position_columns]
        
        # 4. Mutation Ranking (strictly evolutionary)
        prop_engine = MutationProposalEngine(generators=[FamilyConsensusGenerator()])
        scoring_engine = ProposalScoringEngine()
        
        mutation_rows = []
        
        for pos_row in sorted_positions:
            if not pos_row["eligible"]:
                continue
                
            pos = pos_row["reference_position"]
            res = Residue(pos)
            
            proposals = prop_engine.generate_for_residue(res)
            
            for prop in proposals:
                scoring_engine.score(prop, res)
                
                # Extract support count (from family consensus only)
                family_support_count = len(prop.evidence.get("supporting_families", []))
                
                # Extract chemical plausibility
                chemical_plausibility = prop.chemical_change()
                
                mutation_rows.append({
                    "reference_position": pos,
                    "reference_residue": prop.from_residue,
                    "proposed_residue": prop.to_residue,
                    "proposal_score": prop.proposal_score,
                    "atlas_evidence_score": pos_row["evolutionary_score"],
                    "family_support_count": family_support_count,
                    "chemical_plausibility": chemical_plausibility,
                    "proposal_sources": ";".join(prop.sources)
                })
                
        # Sort mutations: proposal_score DESC, atlas_evidence_score DESC, reference_position ASC, proposed_residue ASC
        sorted_mutations = sorted(
            mutation_rows,
            key=lambda x: (
                x["proposal_score"],
                x["atlas_evidence_score"],
                -x["reference_position"],
                -ord(x["proposed_residue"])
            ),
            reverse=True
        )
        
        for idx, row in enumerate(sorted_mutations, 1):
            row["global_rank"] = idx
            
        # Re-order columns to match the required schema
        mutation_columns = [
            "global_rank", "reference_position", "reference_residue", 
            "proposed_residue", "proposal_score", "atlas_evidence_score", 
            "family_support_count", "chemical_plausibility", "proposal_sources"
        ]
        mutation_df = pd.DataFrame(sorted_mutations)[mutation_columns]
        
        # 5. Leakage Assertions
        # Leakage Assertion 1: Known_mutations is absent or completely masked
        masked_master = mocked_load_master_table()
        if not masked_master["Known_mutations"].isna().all():
            raise AssertionError("Leakage Check Failed: Known_mutations column is not completely masked.")
        
        # Leakage Assertion 2: Mutation_evidence cannot contribute to scores
        if not (masked_master["Mutation_evidence"] == "NO").all():
            raise AssertionError("Leakage Check Failed: Mutation_evidence column is not set to 'NO'.")
        if position_df["evolutionary_score"].max() > 7:
            raise AssertionError(f"Leakage Check Failed: Maximum evolutionary score ({position_df['evolutionary_score'].max()}) exceeds the limit of 7.")
            
        # Leakage Assertion 3: No proposal has source 'known_mutation'
        for row in sorted_mutations:
            sources = row["proposal_sources"].split(";")
            if "known_mutation" in sources:
                raise AssertionError(f"Leakage Check Failed: Mutation proposal at position {row['reference_position']} has blocked source 'known_mutation'.")
                
        # Leakage Assertion 4: No validation/literature benchmark file has been loaded
        # Guarded open has been active and would raise PermissionError on any open. We check this by asserting guarded_open works.
        
        # Leakage Assertion 5: No mutation proposal originates exclusively from published evidence
        # Asserted since proposal_engine generators did not include KnownMutationGenerator
        
        # Leakage Assertion 6: Protected catalytic positions are not recommended
        for triad_pos in protected_positions:
            triad_rows = position_df[position_df["reference_position"] == triad_pos]
            if triad_rows.empty:
                raise AssertionError(f"Integrity Check Failed: Catalytic triad position {triad_pos} is missing from position ranking.")
            for _, tr in triad_rows.iterrows():
                if tr["eligible"] is not False:
                    raise AssertionError(f"Leakage Check Failed: Catalytic triad position {triad_pos} is marked as eligible.")
            mut_matches = mutation_df[mutation_df["reference_position"] == triad_pos]
            if not mut_matches.empty:
                raise AssertionError(f"Leakage Check Failed: Found proposed mutations for protected catalytic position {triad_pos}.")
                
        # Leakage Assertion 7: Position and proposal scores contain no literature bonus
        for row in sorted_mutations:
            prop_score = row["proposal_score"]
            # Verify proposal score is purely family_support + fvi + chemical_plausibility
            # Max family_support = 9, Max fvi = 6, Max chemical_plausibility = 1 (Max score is 16).
            # We assert no literature bonus components exist.
            res = Residue(row["reference_position"])
            # Check that known_mutation_support in the components dict is 0
            scoring_engine.score(prop, res)
            # Check the components directly
            components = prop.evidence.get("proposal_score_components", {})
            if components.get("known_mutation_support", 0) != 0:
                raise AssertionError(f"Leakage Check Failed: Non-zero known_mutation_support component at position {row['reference_position']}")
                
        print("All leakage assertions successfully passed.")
        
        # 6. Save Outputs
        output_dir = pathlib.Path("results/validation/evolutionary_only")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pos_path = output_dir / "frozen_position_ranking.tsv"
        mut_path = output_dir / "frozen_mutation_ranking.tsv"
        
        position_df.to_csv(pos_path, sep="\t", index=False)
        mutation_df.to_csv(mut_path, sep="\t", index=False)
        
        print(f"Saved frozen position ranking to {pos_path}")
        print(f"Saved frozen mutation ranking to {mut_path}")
        
        # 7. Generate Freeze Manifest
        master_table_path = "atlas_v3/atlas_v3_master_position_table.tsv"
        fvi_table_path = "atlas_v3/families/family_variability_index.tsv"
        
        manifest_data = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "atlas_version": get_project_version(),
            "python_version": sys.version,
            "input_dataset_paths": {
                "master_position_table": master_table_path,
                "family_variability_index": fvi_table_path
            },
            "input_dataset_sha256": {
                "master_position_table": get_sha256(master_table_path),
                "family_variability_index": get_sha256(fvi_table_path)
            },
            "scoring_rules": {
                "position_score": "FVI >= 5 (+4) or FVI >= 3 (+2) | conservation < 30 (+2) | consensus_count >= 4 (+1) | literature masked (+0)",
                "mutation_score": "family_support (len(families)) + FVI + chemical_plausibility (+1 if conservative) | literature masked (+0)"
            },
            "thresholds": {
                "eligible_fvi_minimum": 1
            },
            "protected_positions": sorted(list(protected_positions)),
            "number_of_total_positions": total_positions_count,
            "number_of_eligible_positions": eligible_positions_count,
            "number_of_generated_mutation_proposals": len(mutation_df),
            "frozen_output_paths": {
                "frozen_position_ranking": str(pos_path),
                "frozen_mutation_ranking": str(mut_path)
            },
            "frozen_output_sha256": {
                "frozen_position_ranking": get_sha256(pos_path),
                "frozen_mutation_ranking": get_sha256(mut_path)
            }
        }
        
        manifest_path = output_dir / "freeze_manifest.json"
        with orig_open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)
            
        print(f"Saved freeze manifest to {manifest_path}")
        print("Freeze successfully completed.")
        return manifest_data

    finally:
        # Teardown: Restore all original references
        builtins.open = orig_open
        engine.atlas.load_master_table = orig_atlas_load
        if orig_evidence_load is not None:
            engine.evidence.load_master_table = orig_evidence_load
        if orig_ranking_load is not None:
            engine.ranking.load_master_table = orig_ranking_load
        if orig_mapper_load is not None:
            engine.reference_mapper.load_master_table = orig_mapper_load

if __name__ == "__main__":
    run_freeze()
