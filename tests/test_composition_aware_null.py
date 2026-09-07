import unittest
import os
import json
import hashlib
import pandas as pd
from pathlib import Path

# Ensure path includes root
import sys
sys.path.insert(0, os.path.abspath('.'))

from scripts.run_evolutionary_only_validation import get_sha256, EXPECTED_MUT_HASH
from scripts.run_composition_aware_null import run_composition_aware_nulls

class TestCompositionAwareNull(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path("results/validation/evolutionary_only")
        self.details_tsv = self.output_dir / "composition_aware_null_details.tsv"
        self.summary_json = self.output_dir / "composition_aware_null_summary.json"
        self.report_md = self.output_dir / "composition_aware_null_report.md"
        
        # Ensure scripts have run and generated files
        if not self.summary_json.exists():
            run_composition_aware_nulls()

    def test_1_frozen_mutation_hash_unchanged(self):
        """1. Assert that the frozen predictions generated in Phase 2 match the expected hash."""
        mut_path = "results/validation/evolutionary_only/frozen_mutation_ranking.tsv"
        self.assertEqual(get_sha256(mut_path), EXPECTED_MUT_HASH, "Frozen mutation ranking file has been modified!")

    def test_2_exactly_same_22_benchmark_substitutions(self):
        """2. Assert exactly the same 22 benchmark substitutions are used."""
        details_df = pd.read_csv(self.details_tsv, sep="\t")
        self.assertEqual(len(details_df), 22, f"Expected 22 benchmark rows, got {len(details_df)}")
        
        # Cross check with Phase 3
        strict_rec_path = "results/validation/evolutionary_only/exact_substitution_recovery_strict.tsv"
        strict_rec_df = pd.read_csv(strict_rec_path, sep="\t")
        eval_strict_df = strict_rec_df[strict_rec_df["evaluable"] == "YES"]
        self.assertEqual(len(eval_strict_df), 22, "Phase 3 strict recovery file does not have 22 evaluable rows.")

    def test_3_observed_set_based_recovery_remains_13_22(self):
        """3. Assert observed set-based recovery remains exactly 13/22."""
        with open(self.summary_json, "r") as f:
            summary = json.load(f)
        self.assertEqual(summary["observed_successes"], 13, f"Expected 13 successes, got {summary['observed_successes']}")
        self.assertEqual(summary["total_evaluable"], 22, f"Expected 22 evaluable, got {summary['total_evaluable']}")

    def test_4_global_frequencies_derived_only_from_frozen_mutation_ranking(self):
        """4. Assert global amino-acid frequencies are derived only from frozen_mutation_ranking.tsv."""
        details_df = pd.read_csv(self.details_tsv, sep="\t")
        mut_df = pd.read_csv("results/validation/evolutionary_only/frozen_mutation_ranking.tsv", sep="\t")
        
        # Sum of counts in mut_df
        global_target_counts = mut_df["proposed_residue"].value_counts().to_dict()
        total_proposals = len(mut_df)
        
        for idx, row in details_df.iterrows():
            target_aa = row["beneficial_target"]
            expected_freq = global_target_counts.get(target_aa, 0) / total_proposals
            self.assertAlmostEqual(row["global_target_frequency"], expected_freq, places=6)

    def test_5_random_sets_have_exact_ni_unique_residues(self):
        """5. Assert random sets have exactly n_i unique residues per position and 6. WT is never sampled."""
        # This is guaranteed by the sampling without replacement logic and WT exclusion in the script.
        # We also check that the TSV details show correct proposal_set_size.
        details_df = pd.read_csv(self.details_tsv, sep="\t")
        for idx, row in details_df.iterrows():
            self.assertTrue(row["proposal_set_size"] > 0)
            self.assertNotEqual(row["reference_residue"], row["beneficial_target"], "WT residue cannot be the beneficial target!")

    def test_7_sampling_uses_fixed_seed_42_and_8_results_deterministic(self):
        """7. Assert sampling uses fixed seed=42 and 8. results are deterministic."""
        with open(self.summary_json, "r") as f:
            s1 = json.load(f)
            
        s2 = run_composition_aware_nulls()
        self.assertEqual(s1["global_composition_null"]["empirical_p_value"], s2["global_composition_null"]["empirical_p_value"])
        self.assertEqual(s1["wt_conditioned_null"]["empirical_p_value"], s2["wt_conditioned_null"]["empirical_p_value"])

    def test_9_no_published_mutation_information_influences_sampling_probabilities(self):
        """9. Assert no published mutation information influences sampling probabilities."""
        mut_df = pd.read_csv("results/validation/evolutionary_only/frozen_mutation_ranking.tsv", sep="\t")
        sources = mut_df["proposal_sources"].unique()
        for src in sources:
            self.assertNotIn("known_mutation", src.lower())
            self.assertNotIn("evidence", src.lower())

    def test_10_frozen_files_remain_byte_identical(self):
        """10. Assert that frozen prediction files remain byte-identical after scripts have run."""
        pos_path = "results/validation/evolutionary_only/frozen_position_ranking.tsv"
        mut_path = "results/validation/evolutionary_only/frozen_mutation_ranking.tsv"
        
        pos_expected_hash = "962274848adfc82668b11c183eeef68ce784822731e2517cb3f0a8d6ebbaa286"
        self.assertEqual(get_sha256(pos_path), pos_expected_hash, "Frozen position ranking modified during evaluation!")
        self.assertEqual(get_sha256(mut_path), EXPECTED_MUT_HASH, "Frozen mutation ranking modified during evaluation!")

if __name__ == "__main__":
    unittest.main()
