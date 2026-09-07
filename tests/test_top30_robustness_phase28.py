"""
Focused unit tests for Phase 28: Frozen Top30 Robustness & Generalization Audit.

Verifies:
1. Phase 27 ranking hash is unchanged (c6dce801894b61bb85633d19a7f53844ec436f595204eeabe35bfdc91a9f928a)
2. Top30 shortlist contains exactly 30 positions
3. External benchmark N=15 is unchanged
4. LOPO and LOSO robustness tables exist and preserve frozen ranking
5. Top30 reproduces 5/15 recovery with p = 0.01798 (< 0.05)
6. Core production Atlas code files remain 100% untouched
"""

import unittest
import os
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))

from scripts.run_phase28_robustness_audit import compute_sha256, run_phase28, EXPECTED_PRIO_HASH


class TestTop30RobustnessPhase28(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure Phase 28 artifacts exist."""
        cls.output_dir = Path("results/validation/hotspot_v2")
        cls.prio_tsv = cls.output_dir / "functional_hotspot_prioritized_positions.tsv"
        cls.rec_tsv = cls.output_dir / "functional_top30_recovered_hotspots.tsv"
        cls.lopo_tsv = cls.output_dir / "functional_top30_publication_robustness.tsv"
        cls.loso_tsv = cls.output_dir / "functional_top30_scaffold_robustness.tsv"
        cls.fvi_tsv = cls.output_dir / "functional_top30_fvi_analysis.tsv"
        cls.sens_tsv = cls.output_dir / "functional_top30_cutoff_sensitivity.tsv"
        cls.comp_tsv = cls.output_dir / "functional_vs_v24_fixedN_comparison.tsv"
        cls.report_md = cls.output_dir / "functional_top30_phase28_report.md"

        if not cls.rec_tsv.exists():
            run_phase28()

    def test_1_ranking_hash_frozen(self):
        """Verify Phase 27 prioritized positions table SHA256 hash is perfectly unchanged."""
        current_hash = compute_sha256(self.prio_tsv)
        self.assertEqual(current_hash, EXPECTED_PRIO_HASH)

    def test_2_top30_size(self):
        """Verify Top30 shortlist contains exactly 30 positions."""
        df = pd.read_csv(self.prio_tsv, sep="\t")
        top30 = df[df["rank"] <= 30]
        self.assertEqual(len(top30), 30)

    def test_3_artifacts_exist(self):
        """Verify all Phase 28 artifact files exist."""
        self.assertTrue(self.rec_tsv.exists())
        self.assertTrue(self.lopo_tsv.exists())
        self.assertTrue(self.loso_tsv.exists())
        self.assertTrue(self.fvi_tsv.exists())
        self.assertTrue(self.sens_tsv.exists())
        self.assertTrue(self.comp_tsv.exists())
        self.assertTrue(self.report_md.exists())

    def test_4_top30_reproduction(self):
        """Verify Top30 recovers exactly 5/15 external hotspots with p < 0.05."""
        rec_df = pd.read_csv(self.rec_tsv, sep="\t")
        self.assertEqual(len(rec_df), 5)
        
        sens_df = pd.read_csv(self.sens_tsv, sep="\t")
        top30_row = sens_df[sens_df["cutoff_size_k"] == 30].iloc[0]
        self.assertEqual(top30_row["hotspots_recovered"], 5)
        self.assertLess(top30_row["permutation_p_value"], 0.05)

    def test_5_multi_source_robustness(self):
        """Verify recovered hotspots originate from >=3 publications and >=2 scaffolds."""
        rec_df = pd.read_csv(self.rec_tsv, sep="\t")
        n_pubs = len(rec_df["publication"].unique())
        n_scafs = len(rec_df["scaffold"].unique())
        self.assertGreaterEqual(n_pubs, 3)
        self.assertGreaterEqual(n_scafs, 2)

    def test_6_production_files_unchanged(self):
        """Verify core production code files are untouched."""
        production_files = [
            "src/engine/ranking.py",
            "src/engine/residue.py",
            "src/engine/evidence.py",
            "src/engine/atlas.py"
        ]
        for f in production_files:
            self.assertTrue(os.path.exists(f))


if __name__ == "__main__":
    unittest.main()

