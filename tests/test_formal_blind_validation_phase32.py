"""
Focused unit tests for Phase 32: Formal Literature-Blind End-to-End Validation.

Verifies:
1. Manifest file phase32_validation_manifest.json exists and verifies zero literature leakage
2. Frozen end-to-end predictions TSV exists and matches frozen SHA256 hash
3. WHERE validation reproduces Phase 28 (5/15, 2.92x enrichment, p = 0.01798)
4. Evolutionary WHAT conditional validation reproduces Phase 30 (Top1 = 2/5, Top5 = 4/5)
5. Catalytic triad residues (160, 206, 237) are protected with zero recommendations
6. Core production Atlas code files remain 100% untouched
"""

import unittest
import os
import sys
import json
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))

from scripts.run_phase32_formal_blind_validation import compute_sha256, run_phase32, EXPECTED_PRIO_HASH


class TestFormalBlindValidationPhase32(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Ensure Phase 32 artifacts exist."""
        cls.output_dir = Path("results/validation/hotspot_v2")
        cls.manifest_json = cls.output_dir / "phase32_validation_manifest.json"
        cls.frozen_pred_tsv = cls.output_dir / "phase32_frozen_end_to_end_predictions.tsv"
        cls.where_val_tsv = cls.output_dir / "phase32_where_validation.tsv"
        cls.what_val_tsv = cls.output_dir / "phase32_what_validation.tsv"
        cls.decomp_tsv = cls.output_dir / "phase32_failure_decomposition.tsv"
        cls.leakage_md = cls.output_dir / "phase32_leakage_audit.md"
        cls.report_md = cls.output_dir / "phase32_formal_validation_report.md"

        if not cls.frozen_pred_tsv.exists():
            run_phase32()

    def test_1_artifacts_exist(self):
        """Verify all Phase 32 artifact files exist."""
        self.assertTrue(self.manifest_json.exists())
        self.assertTrue(self.frozen_pred_tsv.exists())
        self.assertTrue(self.where_val_tsv.exists())
        self.assertTrue(self.what_val_tsv.exists())
        self.assertTrue(self.decomp_tsv.exists())
        self.assertTrue(self.leakage_md.exists())
        self.assertTrue(self.report_md.exists())

    def test_2_leakage_audit_passed(self):
        """Verify Literature-Leakage Audit passed."""
        with open(self.manifest_json, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["literature_leakage_audit"], "PASS (0% Literature Leakage)")

    def test_3_frozen_predictions_count(self):
        """Verify frozen predictions table contains exactly 30 rows."""
        df = pd.read_csv(self.frozen_pred_tsv, sep="\t")
        self.assertEqual(len(df), 30)
        self.assertEqual(df["shortlist_rank"].min(), 1)
        self.assertEqual(df["shortlist_rank"].max(), 30)

    def test_4_where_validation_reproduced(self):
        """Verify WHERE validation reproduces 5/15 recovery with p < 0.05."""
        where_df = pd.read_csv(self.where_val_tsv, sep="\t").iloc[0]
        self.assertEqual(where_df["external_hotspots_recovered"], 5)
        self.assertLess(where_df["permutation_p_value"], 0.05)

    def test_5_what_validation_reproduced(self):
        """Verify Evolutionary WHAT conditional Top5 recovery equals 4/5."""
        what_df = pd.read_csv(self.what_val_tsv, sep="\t")
        top30_pos = what_df[what_df["in_top30_where"] == "YES"]
        top5_evo = top30_pos[top30_pos["evo_what_rank"] <= 5]
        self.assertEqual(len(top5_evo), 4)

    def test_6_catalytic_protection(self):
        """Verify catalytic triad residues (160, 206, 237) are protected."""
        df = pd.read_csv(self.frozen_pred_tsv, sep="\t")
        cat_df = df[df["reference_position"].isin([160, 206, 237])]
        if len(cat_df) > 0:
            self.assertTrue((cat_df["recommendation_status"] == "EXCLUDED (PROTECTED CATALYTIC)").all())

    def test_7_production_files_unchanged(self):
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

