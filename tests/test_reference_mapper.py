import unittest
import json
from engine.study_sequence import StudySequence
from engine.atlas_position import AtlasPosition
from engine.mapping_status import MappingStatus
from engine.mapped_residue import MappedResidue
from engine.mapping_result import MappingResult
from engine.reference_mapper import ReferenceMapper

class TestReferenceMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = ReferenceMapper()
        self.ref_seq = self.mapper.get_reference_sequence()

    def test_get_reference_sequence(self):
        self.assertEqual(len(self.ref_seq), 290)
        self.assertTrue(self.ref_seq.startswith("MNFPRASRLM"))

    def test_reference_mapped_to_itself(self):
        study_seq = StudySequence(self.ref_seq, study_id="ref_wt")
        result = self.mapper.map_sequence(study_seq)
        
        self.assertEqual(result.study_id, "ref_wt")
        self.assertEqual(result.exact_matches, 290)
        self.assertEqual(result.substitutions, 0)
        self.assertEqual(result.insertions, 0)
        self.assertEqual(result.deletions, 0)
        self.assertEqual(result.unmapped_residues, 0)
        self.assertEqual(result.study_length, 290)
        self.assertEqual(result.reference_length, 290)
        self.assertEqual(result.alignment_length, 290)
        self.assertEqual(result.identity_percent, 100.0)
        self.assertEqual(result.study_coverage_percent, 100.0)
        self.assertEqual(result.reference_coverage_percent, 100.0)
        self.assertFalse(result.alignment_is_ambiguous)
        self.assertEqual(len(result.warnings), 0)

        # Count identities are satisfied
        self.assertEqual(result.exact_matches + result.substitutions + result.insertions, result.study_length)
        self.assertEqual(result.exact_matches + result.substitutions + result.deletions, result.reference_length)
        self.assertEqual(result.alignment_length, result.exact_matches + result.substitutions + result.insertions + result.deletions)

    def test_known_substitution_r280a(self):
        # WT residue at position 280 is R. Let's substitute it with A.
        mut_seq = self.ref_seq[:279] + "A" + self.ref_seq[280:]
        study_seq = StudySequence(mut_seq, study_id="R280A")
        result = self.mapper.map_sequence(study_seq)

        self.assertEqual(result.exact_matches, 289)
        self.assertEqual(result.substitutions, 1)
        self.assertEqual(result.insertions, 0)
        self.assertEqual(result.deletions, 0)
        
        # Verify specific mapped residue at position 280 (0-indexed 279 in study)
        mr = result.mapped_residues[279]
        self.assertEqual(mr.study_position, 280)
        self.assertEqual(mr.study_residue, "A")
        self.assertEqual(mr.atlas_position_id, 280)
        self.assertEqual(mr.atlas_reference_residue, "R")
        self.assertEqual(mr.mapping_status, MappingStatus.SUBSTITUTION)

    def test_internal_insertion(self):
        # Insert "X" at index 5 of WT (study length 291)
        mut_seq = self.ref_seq[:5] + "A" + self.ref_seq[5:]
        study_seq = StudySequence(mut_seq, study_id="inserted")
        result = self.mapper.map_sequence(study_seq)

        self.assertEqual(result.exact_matches, 290)
        self.assertEqual(result.substitutions, 0)
        self.assertEqual(result.insertions, 1)
        self.assertEqual(result.deletions, 0)
        self.assertEqual(result.study_length, 291)
        self.assertEqual(result.reference_length, 290)
        self.assertEqual(result.alignment_length, 291)

        # Retrieve insertion mapped residue
        # At index 5 in alignment, study pos 6 is 'A' (inserted)
        mr = result.mapped_residues[5]
        self.assertEqual(mr.mapping_status, MappingStatus.INSERTION)
        self.assertEqual(mr.study_position, 6)
        self.assertEqual(mr.study_residue, "A")
        self.assertIsNone(mr.atlas_position)
        self.assertIsNone(mr.atlas_position_id)

    def test_internal_deletion(self):
        # Delete first residue 'M' (index 0) from WT (study length 289)
        mut_seq = self.ref_seq[1:]
        study_seq = StudySequence(mut_seq, study_id="deleted")
        result = self.mapper.map_sequence(study_seq)

        self.assertEqual(result.exact_matches, 289)
        self.assertEqual(result.substitutions, 0)
        self.assertEqual(result.insertions, 0)
        self.assertEqual(result.deletions, 1)
        self.assertEqual(result.study_length, 289)
        self.assertEqual(result.reference_length, 290)
        self.assertEqual(result.alignment_length, 290)

        # Retrieve deletion mapped residue
        # Alignment index 0 should represent reference deletion
        mr = result.mapped_residues[0]
        self.assertEqual(mr.mapping_status, MappingStatus.DELETION)
        self.assertEqual(mr.atlas_position_id, 1)
        self.assertIsNone(mr.study_position)
        self.assertIsNone(mr.study_residue)

    def test_unsupported_residues_j_u_o(self):
        # WT starts with MNFPRASRLM. We substitute N2 with J, F3 with U, and P4 with O.
        mut_seq = "MJUORASRLM" + self.ref_seq[10:]
        study_seq = StudySequence(mut_seq, study_id="juo_seq")
        result = self.mapper.map_sequence(study_seq)

        # Check warnings generated for J, U, and O
        # Warning positions must use 1-based study coordinates
        comp_warnings = [w for w in result.warnings if isinstance(w, str) and "temporarily replaced" in w]
        self.assertEqual(len(comp_warnings), 3)
        self.assertIn("Character 'J' at study position 2", comp_warnings[0])
        self.assertIn("Character 'U' at study position 3", comp_warnings[1])
        self.assertIn("Character 'O' at study position 4", comp_warnings[2])

        # Verify that original study residues (J, U, O) are recovered and preserved
        self.assertEqual(result.mapped_residues[1].study_residue, "J")
        self.assertEqual(result.mapped_residues[2].study_residue, "U")
        self.assertEqual(result.mapped_residues[3].study_residue, "O")

    def test_multiple_optimal_alignments(self):
        # Aligning "AAAAA" against "AAAA" should trigger multiple optimal gap placement paths
        # Reference length 290 (or similar). Let's construct a smaller query to demonstrate.
        # But wait, ReferenceMapper aligns against the reconstructed full 290-residue reference.
        # Let's align a sequence of "A"*280 + "V"*10 to reference to trigger gap alignment ambiguities.
        # Let's align "A"*295 to reference (forces multiple insertion possibilities).
        study_seq = StudySequence("A" * 295, study_id="poly_a")
        result = self.mapper.map_sequence(study_seq)

        # Check for multiple optimal alignments code in warnings
        self.assertTrue(result.optimal_alignment_count > 1)
        self.assertTrue(result.alignment_is_ambiguous)
        
        codes = [w["code"] for w in result.warnings if isinstance(w, dict)]
        self.assertIn("MULTIPLE_OPTIMAL_ALIGNMENTS", codes)

    def test_deterministic_mapping(self):
        study_seq = StudySequence(self.ref_seq, study_id="det_check")
        res1 = self.mapper.map_sequence(study_seq)
        res2 = self.mapper.map_sequence(study_seq)
        self.assertEqual(res1.alignment_score, res2.alignment_score)
        self.assertEqual(res1.to_json(), res2.to_json())

    def test_inconsistent_counts_rejection(self):
        study_seq = StudySequence(self.ref_seq, study_id="inconsistent_check")
        
        # exact_matches + substitutions + insertions != study_length -> raise ValueError
        with self.assertRaises(ValueError):
            MappingResult(
                study_sequence=study_seq,
                mapped_residues=[],
                alignment_score=100.0,
                exact_matches=100,
                substitutions=0,
                insertions=0,
                deletions=0,
                unmapped_residues=0,
                study_length=290, # study_length is 290, but matches + sub + ins = 100
                reference_length=290,
                alignment_length=100,
                alignment_method="pairwise_global",
                scoring_parameters={},
                reference_sequence_hash="dummy",
                coordinate_system="IsPETase_v1",
                reference_name="IsPETase_v1_reference",
                biopython_version="1.87",
                optimal_alignment_count=1,
                alignment_is_ambiguous=False
            )

if __name__ == "__main__":
    unittest.main()
