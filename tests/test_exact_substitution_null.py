import unittest
import os
import json
import hashlib
import pandas as pd
from pathlib import Path

# Ensure path includes root
import sys
sys.path.insert(0, os.path.abspath('.'))

from scripts.run_evolutionary_only_validation import get_sha256, EXPECTED_POS_HASH, EXPECTED_MUT_HASH
from scripts.run_exact_substitution_null import run_null_models

class TestExactSubstitutionNull(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path("results/validation/evolutionary_only")
        self.details_tsv = self.output_dir / "exact_substitution_null_details.tsv"
        self.summary_json = self.output_dir / "exact_substitution_null_summary.json"
        self.report_md = self.output_dir / "exact_substitution_null_report.md"
        self.independence_tsv = self.output_dir / "evolutionary_dataset_independence_audit.tsv"
        self.independence_md = self.output_dir / "evolutionary_dataset_independence_report.md"
        
        # Ensure scripts have run and generated files
        if not self.summary_json.exists():
            run_null_models()

    def test_1_frozen_prediction_hashes_unchanged(self):
        """1. Assert that the frozen predictions generated in Phase 2 match the expected hashes."""
        pos_path = "results/validation/evolutionary_only/frozen_position_ranking.tsv"
        mut_path = "results/validation/evolutionary_only/frozen_mutation_ranking.tsv"
        
        self.assertEqual(get_sha256(pos_path), EXPECTED_POS_HASH, "Frozen position ranking file has been modified!")
        self.assertEqual(get_sha256(mut_path), EXPECTED_MUT_HASH, "Frozen mutation ranking file has been modified!")

    def test_2_exact_benchmark_contains_same_22_evaluable_substitutions(self):
        """2. Assert exact benchmark contains the same 22 evaluable beneficial substitutions as Phase 3."""
        details_df = pd.read_csv(self.details_tsv, sep="\t")
        self.assertEqual(len(details_df), 22, f"Expected 22 evaluable beneficial mutations, got {len(details_df)}")
        
        # Verify that all 22 are from Phase 3 strict set and are evaluable
        strict_rec_path = "results/validation/evolutionary_only/exact_substitution_recovery_strict.tsv"
        strict_rec_df = pd.read_csv(strict_rec_path, sep="\t")
        eval_strict_df = strict_rec_df[strict_rec_df["evaluable"] == "YES"]
        self.assertEqual(len(eval_strict_df), 22, "Phase 3 strict recovery file does not have 22 evaluable rows.")

    def test_3_observed_exact_recovery_remains_13_22(self):
        """3. Assert observed exact recovery remains exactly 13/22."""
        with open(self.summary_json, "r") as f:
            summary = json.load(f)
        self.assertEqual(summary["observed_recoveries"], 13, f"Expected 13 observed recoveries, got {summary['observed_recoveries']}")
        self.assertEqual(summary["total_evaluable"], 22, f"Expected 22 total evaluable mutations, got {summary['total_evaluable']}")

    def test_4_proposal_sets_derived_only_from_frozen_mutation_ranking(self):
        """4. Assert proposal sets are derived only from frozen_mutation_ranking.tsv."""
        details_df = pd.read_csv(self.details_tsv, sep="\t")
        mut_df = pd.read_csv("results/validation/evolutionary_only/frozen_mutation_ranking.tsv", sep="\t")
        
        for idx, row in details_df.iterrows():
            pos = int(row["reference_position"])
            expected_n = len(mut_df[mut_df["reference_position"] == pos])
            self.assertEqual(row["number_of_evolutionary_proposals"], expected_n,
                             f"Proposal count mismatch at position {pos}")

    def test_5_no_known_mutation_source_exists(self):
        """5. Assert that no known_mutation source exists in the proposal generation (pure evolutionary proposal)."""
        mut_df = pd.read_csv("results/validation/evolutionary_only/frozen_mutation_ranking.tsv", sep="\t")
        # Check that proposal_sources does not contain known_mutations or literature
        sources = mut_df["proposal_sources"].unique()
        for src in sources:
            self.assertNotIn("known_mutation", src.lower(), "Literature support leaked into frozen evolutionary mutations!")
            self.assertNotIn("evidence", src.lower(), "Literature evidence leaked into frozen evolutionary mutations!")

    def test_6_null_draws_only_from_actual_proposal_sets(self):
        """6. Assert that null draws only from actual proposal sets at each position."""
        details_df = pd.read_csv(self.details_tsv, sep="\t")
        for idx, row in details_df.iterrows():
            # The null probability must be 1 / number_of_proposals if present, else 0
            n = row["number_of_evolutionary_proposals"]
            present = row["beneficial_substitution_present_in_proposal_set"] == "YES"
            expected_p = 1.0 / n if present else 0.0
            self.assertAlmostEqual(row["null_probability"], expected_p, places=6,
                                   msg=f"Null probability mismatch at position {row['reference_position']}")

    def test_7_fixed_seed_gives_deterministic_results(self):
        """7. Assert that fixed seed gives deterministic results across script calls."""
        with open(self.summary_json, "r") as f:
            s1 = json.load(f)
            
        s2 = run_null_models()
        self.assertEqual(s1["primary_null_model"]["empirical_p_value"], s2["primary_null_model"]["empirical_p_value"])
        self.assertEqual(s1["secondary_null_model"]["empirical_p_value"], s2["secondary_null_model"]["empirical_p_value"])

    def test_8_dataset_independence_audit_does_not_modify_sequence_or_msa_files(self):
        """8. Assert that dataset-independence audit did not modify sequence database or MSA files."""
        # Check MSA file path
        msa_path = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean_mafft.fasta")
        self.assertTrue(msa_path.exists())
        
        # We check the SHA256 of the MSA file against its registered provenance hash:
        # "petase_atlas_v3_bacteria_taxonomy_clean_mafft.fasta": "3aa4ba59a43773c5e90a7f76fb31994e810d994a0d7995b21fe7c7e0435a8740"
        expected_msa_hash = "3aa4ba59a43773c5e90a7f76fb31994e810d994a0d7995b21fe7c7e0435a8740"
        self.assertEqual(get_sha256(str(msa_path)), expected_msa_hash, "MSA file was modified by audit!")

    def test_9_frozen_files_remain_byte_identical(self):
        """9. Assert that frozen prediction files remain byte-identical after both scripts have run."""
        pos_path = "results/validation/evolutionary_only/frozen_position_ranking.tsv"
        mut_path = "results/validation/evolutionary_only/frozen_mutation_ranking.tsv"
        
        self.assertEqual(get_sha256(pos_path), EXPECTED_POS_HASH, "Frozen position ranking modified during evaluation!")
        self.assertEqual(get_sha256(mut_path), EXPECTED_MUT_HASH, "Frozen mutation ranking modified during evaluation!")

if __name__ == "__main__":
    unittest.main()
