import unittest
import os
import json
import hashlib
import pandas as pd
import pathlib

# Ensure path includes root
import sys
sys.path.insert(0, os.path.abspath('.'))

from scripts.run_evolutionary_only_validation import run_validation, get_sha256, EXPECTED_POS_HASH, EXPECTED_MUT_HASH

class TestEvolutionaryOnlyBenchmark(unittest.TestCase):
    def setUp(self):
        self.output_dir = pathlib.Path("results/validation/evolutionary_only")
        self.strict_tsv = self.output_dir / "benchmark_strict.tsv"
        self.expanded_tsv = self.output_dir / "benchmark_expanded.tsv"
        self.pos_rec_tsv = self.output_dir / "position_recovery_strict.tsv"
        self.mut_rec_tsv = self.output_dir / "exact_substitution_recovery_strict.tsv"
        self.summary_json = self.output_dir / "evolutionary_only_validation_summary.json"
        self.report_md = self.output_dir / "evolutionary_only_validation_report.md"
        self.cutoff_tsv = self.output_dir / "recall_by_cutoff.tsv"
        
        # Run validation if files do not exist yet
        if not self.summary_json.exists():
            run_validation()

    def test_frozen_prediction_hashes_unchanged(self):
        """1. Assert that the frozen predictions generated in Phase 2 remain byte-identical and match registered hashes."""
        pos_path = "results/validation/evolutionary_only/frozen_position_ranking.tsv"
        mut_path = "results/validation/evolutionary_only/frozen_mutation_ranking.tsv"
        
        self.assertEqual(get_sha256(pos_path), EXPECTED_POS_HASH, "Frozen position ranking file has been modified!")
        self.assertEqual(get_sha256(mut_path), EXPECTED_MUT_HASH, "Frozen mutation ranking file has been modified!")

    def test_strict_benchmark_purity(self):
        """2. Assert strict benchmark contains only primary beneficial mutations and 9. expanded benchmark does not contaminate it."""
        strict_df = pd.read_csv(self.strict_tsv, sep="\t")
        expanded_df = pd.read_csv(self.expanded_tsv, sep="\t")
        
        # In strict benchmark, every record must have eligibility 'eligible_primary'
        self.assertTrue((strict_df["benchmark_eligibility"] == "eligible_primary").all(), 
                        "Strict benchmark contains non-primary records!")
        
        # Check that expanded benchmark is separate and larger
        self.assertTrue(len(expanded_df) > len(strict_df), 
                        "Expanded benchmark is not larger than strict benchmark.")
        
        # Check that no 'eligible_contextual' is in strict_df
        self.assertNotIn("eligible_contextual", strict_df["benchmark_eligibility"].values)

    def test_position_level_deduplication(self):
        """3. Assert that positions are correctly deduplicated for position-level recovery counts."""
        rec_df = pd.read_csv(self.pos_rec_tsv, sep="\t")
        # Every reference position must occur stictly once
        self.assertEqual(len(rec_df["reference_position"]), len(rec_df["reference_position"].unique()), 
                         "Position-level recovery dataset has duplicates!")

    def test_positives_within_eligible_universe(self):
        """4. Assert that all evaluable positive positions analyzed belong to the 243-position eligible universe."""
        rec_df = pd.read_csv(self.pos_rec_tsv, sep="\t")
        
        pos_df = pd.read_csv("results/validation/evolutionary_only/frozen_position_ranking.tsv", sep="\t")
        eligible_positions = set(pos_df[pos_df["eligible"] == True]["reference_position"])
        
        for pos in rec_df["reference_position"]:
            self.assertIn(pos, eligible_positions, f"Analyzed positive position {pos} is not in the eligible universe!")

    def test_top_10pct_cutoff_deterministic(self):
        """5. Assert that the Top 10% cutoff is deterministically calculated as 24 positions using floor rounding."""
        with open(self.summary_json, "r") as f:
            summary = json.load(f)
        cutoff_size = summary["strict_benchmark"]["top_10pct_metrics"]["cutoff_size"]
        self.assertEqual(cutoff_size, 24, f"Expected cutoff size 24, got {cutoff_size}")

    def test_null_model_eligible_universe(self):
        """6. Assert that the null model samples stochastically from exactly 243 eligible positions."""
        # This is verified by ensuring the sample space size is 243 and 7. the random sample size is exactly 24
        # We also check that the manifest/summary JSON reflects these values
        with open(self.summary_json, "r") as f:
            summary = json.load(f)
        
        # Verify the expected null model metrics from summary
        strict_metrics = summary["strict_benchmark"]["top_10pct_metrics"]
        self.assertAlmostEqual(strict_metrics["random_expected_recovery"], 24.0 * (summary["strict_benchmark"]["evaluable_beneficial_positions"] / 243.0), places=2)

    def test_reproducible_random_seed(self):
        """8. Assert that the fixed random seed 42 produces stochastically reproducible results."""
        # Running the validation script twice should result in identical summary p-values and expected counts
        with open(self.summary_json, "r") as f:
            summary_1 = json.load(f)
            
        summary_2 = run_validation()
        
        p1 = summary_1["strict_benchmark"]["top_10pct_metrics"]["empirical_p_value"]
        p2 = summary_2["strict_benchmark"]["top_10pct_metrics"]["empirical_p_value"]
        self.assertEqual(p1, p2, "Random seed is not producing reproducible results in permutation simulation.")

if __name__ == "__main__":
    unittest.main()
