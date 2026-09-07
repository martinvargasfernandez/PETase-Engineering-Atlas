import unittest
import os
import json
import hashlib
import pandas as pd
import pathlib

# Ensure path includes root
import sys
sys.path.insert(0, os.path.abspath('.'))

from scripts.run_evolutionary_only_freeze import run_freeze, get_sha256

class TestEvolutionaryOnlyFreeze(unittest.TestCase):
    def setUp(self):
        self.output_dir = pathlib.Path("results/validation/evolutionary_only")
        self.pos_path = self.output_dir / "frozen_position_ranking.tsv"
        self.mut_path = self.output_dir / "frozen_mutation_ranking.tsv"
        self.manifest_path = self.output_dir / "freeze_manifest.json"

    def test_run_freeze_execution(self):
        """Run the freeze script and verify manifest details."""
        manifest = run_freeze()
        
        self.assertTrue(self.pos_path.exists())
        self.assertTrue(self.mut_path.exists())
        self.assertTrue(self.manifest_path.exists())
        
        # Verify universe boundaries from manifest
        self.assertEqual(manifest["number_of_total_positions"], 290)
        self.assertEqual(manifest["number_of_eligible_positions"], 243)
        self.assertEqual(len(manifest["protected_positions"]), 3)
        self.assertListEqual(manifest["protected_positions"], [160, 206, 237])

    def test_frozen_position_properties(self):
        """Verify position-level ranking properties and leakage prevention."""
        run_freeze()
        df = pd.read_csv(self.pos_path, sep="\t")
        
        # Verify row count
        self.assertEqual(len(df), 290)
        
        # Verify columns
        expected_cols = [
            "rank", "reference_position", "reference_residue", "fvi", 
            "global_conservation", "consensus_residue_count", 
            "evolutionary_score", "eligible", "exclusion_reason"
        ]
        self.assertListEqual(list(df.columns), expected_cols)
        
        # Verify sorting order: rank must be 1 to 290 in order
        self.assertListEqual(list(df["rank"]), list(range(1, 291)))
        
        # Assert no evolutionary_score exceeds 7 (FVI: 4, conservation: 2, consensus: 1)
        self.assertTrue((df["evolutionary_score"] <= 7).all())
        
        # Check catalytic triad positions are marked ineligible
        for triad_pos in [160, 206, 237]:
            triad_rows = df[df["reference_position"] == triad_pos]
            self.assertFalse(triad_rows.empty)
            for _, r in triad_rows.iterrows():
                self.assertFalse(r["eligible"])
                self.assertEqual(r["exclusion_reason"], "Catalytic triad control")
                
        # Check FVI=0 exclusions
        fvi_zero_rows = df[df["fvi"] == 0]
        for _, r in fvi_zero_rows.iterrows():
            self.assertFalse(r["eligible"])
            self.assertIn(r["exclusion_reason"], ["Catalytic triad control", "FVI=0 exclusion"])

    def test_frozen_mutation_properties(self):
        """Verify mutation-level proposals and check for literature leakage."""
        run_freeze()
        df = pd.read_csv(self.mut_path, sep="\t")
        
        # Verify columns
        expected_cols = [
            "global_rank", "reference_position", "reference_residue", 
            "proposed_residue", "proposal_score", "atlas_evidence_score", 
            "family_support_count", "chemical_plausibility", "proposal_sources"
        ]
        self.assertListEqual(list(df.columns), expected_cols)
        
        # Assert no known_mutation exists in proposal_sources
        for idx, row in df.iterrows():
            sources = str(row["proposal_sources"]).split(";")
            self.assertNotIn("known_mutation", sources)
            
        # Assert no catalytic triad positions have proposals recommended
        triad_muts = df[df["reference_position"].isin([160, 206, 237])]
        self.assertTrue(triad_muts.empty, "Triad mutation proposals leaked into frozen mutation ranking.")

    def test_deterministic_reproducibility(self):
        """Running the freeze twice must produce identical SHA256 file hashes."""
        run_freeze()
        hash_pos_1 = get_sha256(self.pos_path)
        hash_mut_1 = get_sha256(self.mut_path)
        
        # Re-run freeze
        run_freeze()
        hash_pos_2 = get_sha256(self.pos_path)
        hash_mut_2 = get_sha256(self.mut_path)
        
        self.assertEqual(hash_pos_1, hash_pos_2, "Position ranking output is not deterministically reproducible.")
        self.assertEqual(hash_mut_1, hash_mut_2, "Mutation ranking output is not deterministically reproducible.")

if __name__ == "__main__":
    unittest.main()
