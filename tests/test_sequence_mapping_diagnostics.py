import unittest
import json
from engine.study_sequence import StudySequence
from engine.atlas_position import AtlasPosition
from engine.mapping_status import MappingStatus
from engine.mapped_residue import MappedResidue
from engine.mapping_result import MappingResult
from engine.reference_mapper import ReferenceMapper
from engine.sequence_analyzer import SequenceAnalyzer
from engine.projected_residue import ProjectedResidue

class TestSequenceMappingDiagnostics(unittest.TestCase):
    def setUp(self):
        self.mapper = ReferenceMapper()
        self.ref_seq = self.mapper.get_reference_sequence()
        self.analyzer = SequenceAnalyzer()

    def test_exact_reference_mapping(self):
        # Exact reference sequence mapping
        study_seq = StudySequence(self.ref_seq, study_id="ref_exact")
        result = self.analyzer.analyze(study_seq)

        # Basic diagnostics
        self.assertEqual(result.query_sequence_length, 290)
        self.assertEqual(result.reference_sequence_length, 290)
        self.assertEqual(result.aligned_query_residues, 290)
        self.assertEqual(result.mapped_atlas_positions, 290)
        self.assertEqual(result.sequence_identity, 1.0)
        self.assertEqual(result.query_coverage, 1.0)
        self.assertEqual(result.reference_coverage, 1.0)
        self.assertEqual(result.number_of_insertions, 0)
        self.assertEqual(result.number_of_deletions, 0)
        self.assertEqual(result.number_of_unmapped_query_residues, 0)
        self.assertEqual(result.number_of_unmapped_atlas_positions, 0)
        
        # Warnings and states
        self.assertEqual(len(result.mapping_quality_warnings), 0)
        for pr in result.projected_sequence.projected_residues:
            if pr.mapping_status != MappingStatus.DELETION:
                self.assertEqual(pr.query_mapping_state, "mapped")

    def test_single_substitution(self):
        # Substitution at index 279 (R280A)
        mut_seq = self.ref_seq[:279] + "A" + self.ref_seq[280:]
        study_seq = StudySequence(mut_seq, study_id="ref_mut")
        result = self.analyzer.analyze(study_seq)

        # Diagnostics checks
        self.assertEqual(result.query_sequence_length, 290)
        self.assertEqual(result.reference_sequence_length, 290)
        self.assertEqual(result.aligned_query_residues, 290)
        self.assertEqual(result.mapped_atlas_positions, 290)
        self.assertEqual(result.sequence_identity, 289 / 290)
        self.assertEqual(result.query_coverage, 1.0)
        self.assertEqual(result.reference_coverage, 1.0)
        self.assertEqual(result.number_of_insertions, 0)
        self.assertEqual(result.number_of_deletions, 0)
        self.assertEqual(result.number_of_unmapped_query_residues, 0)
        self.assertEqual(result.number_of_unmapped_atlas_positions, 0)
        self.assertEqual(len(result.mapping_quality_warnings), 0)

        # Residue 280 should be substitution
        res_table = result.to_table()
        r280 = res_table[279]
        self.assertEqual(r280["mapping_status"], "substitution")
        self.assertEqual(r280["query_mapping_state"], "mapped")
        self.assertEqual(r280["atlas_position_id"], 280)

    def test_one_insertion(self):
        # Insert 'A' at index 5
        mut_seq = self.ref_seq[:5] + "A" + self.ref_seq[5:]
        study_seq = StudySequence(mut_seq, study_id="ref_ins")
        result = self.analyzer.analyze(study_seq)

        # Diagnostics checks
        self.assertEqual(result.query_sequence_length, 291)
        self.assertEqual(result.reference_sequence_length, 290)
        self.assertEqual(result.aligned_query_residues, 290)
        self.assertEqual(result.mapped_atlas_positions, 290)
        self.assertEqual(result.sequence_identity, 1.0)
        self.assertEqual(result.query_coverage, 290 / 291)
        self.assertEqual(result.reference_coverage, 1.0)
        self.assertEqual(result.number_of_insertions, 1)
        self.assertEqual(result.number_of_deletions, 0)
        self.assertEqual(result.number_of_unmapped_query_residues, 0)
        self.assertEqual(result.number_of_unmapped_atlas_positions, 0)

        # Warnings: incomplete query coverage, insertions detected
        self.assertIn("incomplete query coverage", result.mapping_quality_warnings)
        self.assertIn("insertions detected", result.mapping_quality_warnings)

        # Insertion residue state checks
        ins_pr = result.projected_sequence.projected_residues[5]
        self.assertEqual(ins_pr.mapping_status, MappingStatus.INSERTION)
        self.assertEqual(ins_pr.query_mapping_state, "insertion")
        self.assertIsNone(ins_pr.atlas_position_id)

    def test_one_deletion(self):
        # Delete first residue 'M' (index 0) from WT
        mut_seq = self.ref_seq[1:]
        study_seq = StudySequence(mut_seq, study_id="ref_del")
        result = self.analyzer.analyze(study_seq)

        # Diagnostics checks
        self.assertEqual(result.query_sequence_length, 289)
        self.assertEqual(result.reference_sequence_length, 290)
        self.assertEqual(result.aligned_query_residues, 289)
        self.assertEqual(result.mapped_atlas_positions, 289)
        self.assertEqual(result.sequence_identity, 1.0)
        self.assertEqual(result.query_coverage, 1.0)
        self.assertEqual(result.reference_coverage, 289 / 290)
        self.assertEqual(result.number_of_insertions, 0)
        self.assertEqual(result.number_of_deletions, 1)
        self.assertEqual(result.number_of_unmapped_query_residues, 0)
        self.assertEqual(result.number_of_unmapped_atlas_positions, 1) # Deletion position is unmapped Reference position

        # Warnings: incomplete reference coverage, deletions detected
        self.assertIn("incomplete reference coverage", result.mapping_quality_warnings)
        self.assertIn("deletions detected", result.mapping_quality_warnings)

        # Deletion row check
        del_pr = result.projected_sequence.projected_residues[0]
        self.assertEqual(del_pr.mapping_status, MappingStatus.DELETION)
        self.assertIsNone(del_pr.query_mapping_state) # Deletion is not a query residue, so query_mapping_state is None
        self.assertEqual(del_pr.atlas_position_id, 1)

    def test_multiple_insertions_deletions(self):
        # Insert 'A' at index 5, and delete first residue 'M' (index 0)
        mut_seq = self.ref_seq[1:5] + "A" + self.ref_seq[5:]
        study_seq = StudySequence(mut_seq, study_id="ref_multi_indel")
        result = self.analyzer.analyze(study_seq)

        self.assertEqual(result.query_sequence_length, 290)
        self.assertEqual(result.reference_sequence_length, 290)
        self.assertEqual(result.aligned_query_residues, 289)
        self.assertEqual(result.mapped_atlas_positions, 289)
        self.assertEqual(result.number_of_insertions, 1)
        self.assertEqual(result.number_of_deletions, 1)
        self.assertEqual(result.number_of_unmapped_atlas_positions, 1)

        self.assertIn("incomplete query coverage", result.mapping_quality_warnings)
        self.assertIn("incomplete reference coverage", result.mapping_quality_warnings)
        self.assertIn("insertions detected", result.mapping_quality_warnings)
        self.assertIn("deletions detected", result.mapping_quality_warnings)

    def test_partial_sequence(self):
        # First 50 residues only
        mut_seq = self.ref_seq[:50]
        study_seq = StudySequence(mut_seq, study_id="partial")
        result = self.analyzer.analyze(study_seq)

        self.assertEqual(result.query_sequence_length, 50)
        self.assertEqual(result.reference_sequence_length, 290)
        self.assertEqual(result.aligned_query_residues, 50)
        self.assertEqual(result.mapped_atlas_positions, 50)
        self.assertEqual(result.query_coverage, 1.0)
        self.assertEqual(result.reference_coverage, 50 / 290)
        self.assertEqual(result.number_of_deletions, 240)
        self.assertEqual(result.number_of_unmapped_atlas_positions, 240)

        self.assertIn("incomplete reference coverage", result.mapping_quality_warnings)
        self.assertIn("deletions detected", result.mapping_quality_warnings)

    def test_evidence_integrity_safeguards(self):
        # We check both insertion and unmapped residues.
        study_seq = StudySequence(self.ref_seq[:10] + "A" + self.ref_seq[10:], study_id="integrity_test")
        result = self.analyzer.analyze(study_seq)

        # Insertion residue is at index 10
        ins_pr = result.projected_sequence.projected_residues[10]
        self.assertEqual(ins_pr.query_mapping_state, "insertion")
        self.assertIsNone(ins_pr.atlas_position_id)

        # Verify all evidence fields return None or empty collections
        self.assertIsNone(ins_pr.global_consensus)
        self.assertIsNone(ins_pr.global_conservation)
        self.assertIsNone(ins_pr.fvi)
        self.assertIsNone(ins_pr.consensus_residues)
        self.assertEqual(ins_pr.family_consensus, {})
        self.assertIsNone(ins_pr.known_mutations)
        self.assertIsNone(ins_pr.mutation_evidence)
        self.assertIsNone(ins_pr.atlas_evidence_score)
        self.assertIsNone(ins_pr.max_score)
        self.assertEqual(ins_pr.score_components, [])
        self.assertIsNone(ins_pr.priority)
        self.assertIsNone(ins_pr.interpretation)

        # Unmapped residue verification
        mr = MappedResidue(
            study_sequence=study_seq,
            mapping_status=MappingStatus.UNMAPPED,
            study_position=1,
            study_residue="M",
            atlas_position=None
        )
        unmapped_pr = ProjectedResidue(mr)
        self.assertEqual(unmapped_pr.query_mapping_state, "unmapped")
        self.assertIsNone(unmapped_pr.atlas_position_id)

        self.assertIsNone(unmapped_pr.global_consensus)
        self.assertIsNone(unmapped_pr.global_conservation)
        self.assertIsNone(unmapped_pr.fvi)
        self.assertIsNone(unmapped_pr.consensus_residues)
        self.assertEqual(unmapped_pr.family_consensus, {})
        self.assertIsNone(unmapped_pr.known_mutations)
        self.assertIsNone(unmapped_pr.mutation_evidence)
        self.assertIsNone(unmapped_pr.atlas_evidence_score)
        self.assertIsNone(unmapped_pr.max_score)
        self.assertEqual(unmapped_pr.score_components, [])
        self.assertIsNone(unmapped_pr.priority)
        self.assertIsNone(unmapped_pr.interpretation)

    def test_serialization(self):
        study_seq = StudySequence(self.ref_seq[:279] + "A" + self.ref_seq[280:], study_id="serial_test") # 1 substitution
        result = self.analyzer.analyze(study_seq)

        d = result.to_dict(include_residue_table=True)
        # Check mapping quality diagnostics exist in dict
        self.assertIn("mapping_quality", d)
        mq = d["mapping_quality"]
        self.assertEqual(mq["query_sequence_length"], 290)
        self.assertEqual(mq["reference_sequence_length"], 290)
        self.assertEqual(mq["aligned_query_residues"], 290)
        self.assertEqual(mq["mapped_atlas_positions"], 290)
        self.assertEqual(mq["sequence_identity"], 289 / 290)
        self.assertEqual(mq["query_coverage"], 1.0)
        self.assertEqual(mq["reference_coverage"], 1.0)
        self.assertEqual(mq["number_of_insertions"], 0)
        self.assertEqual(mq["number_of_deletions"], 0)
        self.assertEqual(mq["number_of_unmapped_query_residues"], 0)
        self.assertEqual(mq["number_of_unmapped_atlas_positions"], 0)
        self.assertEqual(len(mq["mapping_quality_warnings"]), 0)

        # Check query_mapping_state in residue table
        self.assertIn("residue_table", d)
        for row in d["residue_table"]:
            if row["mapping_status"] != "deletion":
                self.assertEqual(row["query_mapping_state"], "mapped")

        # JSON checks
        js = result.to_json()
        loaded = json.loads(js)
        self.assertIn("mapping_quality", loaded)

    def test_backward_compatibility(self):
        study_seq = StudySequence(self.ref_seq, study_id="compat_test")
        result = self.analyzer.analyze(study_seq)

        d = result.to_dict()
        # Verify old fields in 'mapping' dict remain intact
        self.assertEqual(d["mapping"]["alignment_score"], result.mapping_result.alignment_score)
        self.assertEqual(d["mapping"]["identity_percent"], result.mapping_result.identity_percent)
        self.assertEqual(d["mapping"]["study_coverage_percent"], result.mapping_result.study_coverage_percent)
        self.assertEqual(d["mapping"]["reference_coverage_percent"], result.mapping_result.reference_coverage_percent)
        self.assertEqual(d["mapping"]["exact_matches"], result.mapping_result.exact_matches)
        self.assertEqual(d["mapping"]["substitutions"], result.mapping_result.substitutions)
        self.assertEqual(d["mapping"]["insertions"], result.mapping_result.insertions)
        self.assertEqual(d["mapping"]["deletions"], result.mapping_result.deletions)

if __name__ == "__main__":
    unittest.main()
