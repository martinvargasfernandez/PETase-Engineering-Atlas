from engine.sequence_mapping_strategy import SequenceMappingStrategy
from engine.transient_sequence_session import TransientSequenceSession

class SequenceAnalysisEngine:
    """
    Orchestrates the sequence analysis pipeline (validation, coordinate mapping,
    evidence projection, family classification, and transient mutation recommendation).
    Does not require database persistence or persistent Project directories.
    """
    def __init__(
        self,
        mapping_strategy: SequenceMappingStrategy = None,
        evidence_projector = None,
        family_classifier = None
    ):
        from engine.pairwise_reference_mapper import PairwiseReferenceMapper
        from engine.sequence_evidence_projector import SequenceEvidenceProjector
        from engine.family_classifier import FamilyClassifier

        from engine.mutation_proposal_engine import MutationProposalEngine
        from engine.proposal_scoring import ProposalScoringEngine
        from engine.mutation_ranking import MutationRankingEngine
        from engine.proposal_generators.family_consensus_generator import FamilyConsensusGenerator
        from engine.proposal_generators.known_mutation_generator import KnownMutationGenerator

        self.mapping_strategy = mapping_strategy or PairwiseReferenceMapper()
        self.evidence_projector = evidence_projector or SequenceEvidenceProjector
        self.family_classifier = family_classifier or FamilyClassifier()

        self.proposal_engine = MutationProposalEngine(
            generators=[
                FamilyConsensusGenerator(),
                KnownMutationGenerator(),
            ]
        )
        self.scoring_engine = ProposalScoringEngine()
        self.ranking_engine = MutationRankingEngine()

    def analyze_sequence(
        self,
        raw_sequence: str,
        fasta_header: str = None,
        minimum_fvi: int = 1,
        excluded_positions: list = None
    ) -> TransientSequenceSession:
        """
        Runs validation, mapping strategy, projects evidence, classifies the sequence,
        generates mutation proposals, scores them, and compiles the transient session.
        """
        from engine.sequence_validation import normalize_sequence, validate_sequence
        from engine.study_sequence import StudySequence
        from engine.candidate_discovery import CandidateDiscoveryEngine
        from engine.mapping_status import MappingStatus
        from engine.residue import Residue
        from engine.evidence_explanation import EvidenceExplanation

        # 1. Normalize, Validate, and Build StudySequence model
        study_sequence = StudySequence(
            raw_sequence=raw_sequence,
            fasta_header=fasta_header,
            study_id="transient_query"
        )

        # 3. Coordinate Mapping
        mapping_result = self.mapping_strategy.map_sequence(study_sequence)

        # 4. Evidence Projection
        if hasattr(self.evidence_projector, "project"):
            projected_sequence = self.evidence_projector.project(mapping_result)
        else:
            projected_sequence = self.evidence_projector(mapping_result)

        # 5. Family Classification
        family_classification = self.family_classifier.classify(projected_sequence)
        pred_fam = family_classification.predicted_family

        # 6. Candidate Discovery Filter
        discovery_engine = CandidateDiscoveryEngine(
            min_fvi=minimum_fvi,
            exclude_positions=excluded_positions
        )
        candidate_atlas_positions = set(discovery_engine.get_positions())

        # 7. Generate Recommendations for mapped positions
        all_proposals_dicts = []
        
        for mr in mapping_result.mapped_residues:
            # Skip deletions and unmapped coordinates
            if mr.mapping_status == MappingStatus.DELETION or mr.atlas_position is None:
                continue
            
            atlas_pos = mr.atlas_position.atlas_position_id
            
            # Check candidate discovery constraints
            if atlas_pos not in candidate_atlas_positions:
                continue
                
            study_pos = mr.study_position
            curr_res = mr.study_residue
            residue = Residue(atlas_pos)

            # Generate proposals
            proposals = self.proposal_engine.generate_for_residue(residue)

            global_ev = {
                "fvi": residue.fvi,
                "global_conservation": residue.global_conservation,
                "global_consensus": residue.global_consensus,
                "known_mutations": residue.known_mutations or []
            }
            family_ev = {
                "predicted_family": pred_fam,
                "family_consensus": residue.family_consensus
            }

            # Contradictory tags (simulation contradictory tags are empty for transient session)
            position_contradictory = []
            if residue.fvi is not None and residue.fvi <= 1:
                position_contradictory.append("evolutionary_conservation")

            for prop in proposals:
                scored_prop = self.scoring_engine.score(prop, residue)
                
                # Determine supporting tags
                supporting_tags = []
                
                # 1. Known mutation support
                is_known = False
                known_list = residue.known_mutations
                if isinstance(known_list, str):
                    known_list = [k.strip() for k in known_list.split(",") if k.strip()]
                if isinstance(known_list, (list, tuple, set)):
                    for km in known_list:
                        if isinstance(km, dict) and km.get("mutant") == prop.to_residue:
                            is_known = True
                            break
                        elif isinstance(km, str) and len(km) > 0 and km[-1] == prop.to_residue:
                            is_known = True
                            break
                if is_known or "known_mutation" in scored_prop.sources:
                    supporting_tags.append("known_mutation_support")

                # 2. Family consensus support
                if pred_fam in residue.family_consensus and residue.family_consensus[pred_fam] == prop.to_residue:
                    supporting_tags.append("family_consensus_support")

                # 3. Chemical conservative change
                if prop.is_conservative():
                    supporting_tags.append("conservative_substitution")

                contradictory_tags = list(position_contradictory)

                # Formulate qualitative interpretation
                interpretation = (
                    f"Position {atlas_pos} (study position {study_pos}) analyzed. "
                    f"Best proposed mutation: {prop.label} (Score: {prop.proposal_score}, Priority: {prop.proposal_priority}). "
                    f"Atlas Evidence Score: {residue.atlas_evidence_score}. "
                )
                if supporting_tags:
                    interpretation += f"Supported by: {', '.join(supporting_tags)}. "
                if contradictory_tags:
                    interpretation += f"Caution advised due to: {', '.join(contradictory_tags)}. "
                else:
                    interpretation += "No major simulation/evolutionary contradictions detected. "
                interpretation += "Note: Recommendations are qualitative; mutations do not automatically guarantee improved enzyme activity."

                # Construct clean factual EvidenceExplanation
                supporting_list = []
                if residue.atlas_evidence_score is not None:
                    if residue.atlas_evidence_score >= 8:
                        supporting_list.append(f"High Atlas Evidence Score: {residue.atlas_evidence_score}")
                    elif residue.atlas_evidence_score >= 4:
                        supporting_list.append(f"Moderate Atlas Evidence Score: {residue.atlas_evidence_score}")
                
                if residue.fvi is not None:
                    if residue.fvi >= 4:
                        supporting_list.append(f"High family variability: FVI {residue.fvi}")
                    elif residue.fvi <= 2:
                        supporting_list.append(f"Low family variability: FVI {residue.fvi}")
                
                if residue.global_conservation is not None:
                    if residue.global_conservation < 30.0:
                        supporting_list.append("Low global conservation represented in the Atlas score")
                    elif residue.global_conservation >= 70.0:
                        supporting_list.append("High global conservation represented in the Atlas score")

                if pred_fam in residue.family_consensus and residue.family_consensus[pred_fam] == prop.to_residue:
                    supporting_list.append("Family-consensus proposal")

                is_exact_published = False
                any_published_at_pos = False
                matched_km_exact = None
                matched_km_related = None
                
                if isinstance(known_list, (list, tuple, set)):
                    for km in known_list:
                        mutant_char = None
                        km_str = ""
                        if isinstance(km, dict):
                            mutant_char = km.get("mutant")
                            km_str = f"{km.get('source', '')}:{km.get('mutation_label', '')}"
                        elif isinstance(km, str):
                            km_str = km
                            if len(km) > 0:
                                mutant_char = km[-1]
                        
                        if mutant_char is not None:
                            any_published_at_pos = True
                            if mutant_char == prop.to_residue:
                                is_exact_published = True
                                matched_km_exact = km_str
                            else:
                                matched_km_related = km_str

                if is_exact_published:
                    supporting_list.append(f"exact proposed mutation is published: {matched_km_exact}")
                elif any_published_at_pos:
                    supporting_list.append(f"published related mutation at the same position: {matched_km_related}")

                if prop.is_conservative():
                    supporting_list.append(f"Conservative substitution: {prop.from_residue} to {prop.to_residue}")

                missing_list = ["no matched mutant-vs-reference simulation", "no structural evidence", "no experimental evidence"]
                if not is_exact_published:
                    missing_list.append("exact proposed mutation lacks experimental validation")

                explanation = EvidenceExplanation(
                    supporting_evidence=supporting_list,
                    contradictory_evidence=contradictory_tags,
                    missing_evidence=missing_list,
                    final_interpretation=interpretation
                )

                # Determine actionability
                if prop.to_residue == curr_res:
                    mutation_actionability = "already_present"
                    project_mutation_label = None
                else:
                    mutation_actionability = "actionable"
                    project_mutation_label = f"{curr_res}{study_pos}{prop.to_residue}"

                # Append transient proposal record
                all_proposals_dicts.append({
                    "position": atlas_pos,
                    "study_position": study_pos,
                    "wild_type": prop.from_residue,
                    "proposed_mutant": prop.to_residue,
                    "mutation_label": prop.label,
                    "candidate": prop.label,
                    "proposal_score": prop.proposal_score,
                    "proposal_priority": prop.proposal_priority,
                    "atlas_evidence_score": residue.atlas_evidence_score,
                    "sources": prop.sources,
                    "global_evidence": global_ev,
                    "family_evidence": family_ev,
                    "simulation_evidence": [],
                    "structural_evidence": [],
                    "experimental_evidence": [],
                    "supporting_evidence": supporting_tags,
                    "contradictory_evidence": contradictory_tags,
                    "active_case_study_ids": [],
                    "interpretation": interpretation,
                    "warnings": [],
                    "evidence_explanation": explanation.to_dict(),
                    "atlas_mutation_label": prop.label,
                    "project_mutation_label": project_mutation_label,
                    "atlas_reference_residue": prop.from_residue,
                    "study_current_residue": curr_res or "N/A",
                    "proposed_target_residue": prop.to_residue,
                    "mutation_actionability": mutation_actionability
                })

        # Rank the recommendations
        ranked_proposals = self.ranking_engine.rank_by_position(all_proposals_dicts)
        
        # Compile transient recommendations list
        recommendations = []
        for row in ranked_proposals:
            recommendations.append({
                "atlas_position": row["position"],
                "study_position": row["study_position"],
                "wild_type": row["wild_type"],
                "reference_residue": row["wild_type"],
                "proposed_mutant": row["proposed_mutant"],
                "mutation_label": row["mutation_label"],
                "proposal_score": row["proposal_score"],
                "proposal_priority": row["proposal_priority"],
                "atlas_evidence_score": row["atlas_evidence_score"],
                "global_evidence": row["global_evidence"],
                "family_evidence": row["family_evidence"],
                "simulation_evidence": [],
                "structural_evidence": [],
                "experimental_evidence": [],
                "supporting_evidence": row["supporting_evidence"],
                "contradictory_evidence": row["contradictory_evidence"],
                "active_case_study_ids": [],
                "alternatives": row.get("alternative_candidates_with_sources", []),
                "interpretation": row["interpretation"],
                "warnings": row["warnings"],
                "evidence_explanation": row["evidence_explanation"],
                "atlas_mutation_label": row["atlas_mutation_label"],
                "project_mutation_label": row["project_mutation_label"],
                "atlas_reference_residue": row["atlas_reference_residue"],
                "study_current_residue": row["study_current_residue"],
                "proposed_target_residue": row["proposed_target_residue"],
                "mutation_actionability": row["mutation_actionability"]
            })

        # 8. Compute Function-First WHERE Top30 & Evolutionary WHAT proposals
        from engine.functional_hotspots import FunctionFirstEngine
        ff_engine = FunctionFirstEngine()
        function_first_hotspots = ff_engine.project_top30_for_mapping(mapping_result)

        return TransientSequenceSession(
            study_sequence=study_sequence,
            mapping_result=mapping_result,
            projected_sequence=projected_sequence,
            family_classification=family_classification,
            recommendations=recommendations,
            atlas_coordinate_system=self.mapping_strategy._mapper.coordinate_system if hasattr(self.mapping_strategy, "_mapper") else "IsPETase_v1",
            function_first_hotspots=function_first_hotspots
        )
