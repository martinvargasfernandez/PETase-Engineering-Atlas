from typing import List, Dict, Any
from engine.project import Project
from engine.case_study_status import CaseStudyStatus
from engine.residue import Residue
from engine.candidate_discovery import CandidateDiscoveryEngine
from engine.mutation_proposal_engine import MutationProposalEngine
from engine.proposal_scoring import ProposalScoringEngine
from engine.mutation_ranking import MutationRankingEngine
from engine.project_evidence_context import ProjectEvidenceContext
from engine.engineering_recommendation_result import EngineeringRecommendationResult
from engine.evidence_explanation import EvidenceExplanation

class ProjectEngineeringEngine:
    """
    Scientific engine orchestrating candidate discovery, mutation proposal,
    scoring, CaseStudy evidence aggregation, and qualitative ranking.
    """
    def __init__(self):
        from engine.proposal_generators.family_consensus_generator import FamilyConsensusGenerator
        from engine.proposal_generators.known_mutation_generator import KnownMutationGenerator
        
        self.proposal_engine = MutationProposalEngine(
            generators=[
                FamilyConsensusGenerator(),
                KnownMutationGenerator(),
            ]
        )
        self.scoring_engine = ProposalScoringEngine()
        self.ranking_engine = MutationRankingEngine()

    def analyze(
        self,
        project: Project,
        include_case_study_statuses: List[CaseStudyStatus] = None,
        excluded_atlas_positions: List[int] = None,
        minimum_fvi: int = None
    ) -> EngineeringRecommendationResult:
        
        # 1. Load project evidence context
        context = ProjectEvidenceContext(project, statuses=include_case_study_statuses)
        
        # 2. Discover Atlas positions
        min_fvi_val = minimum_fvi if minimum_fvi is not None else 1
        discovery_engine = CandidateDiscoveryEngine(
            min_fvi=min_fvi_val,
            exclude_positions=excluded_atlas_positions
        )
        atlas_positions = discovery_engine.get_positions()

        # 3. Align positions to study sequence coordinates
        positions_to_analyze = []
        for pos in atlas_positions:
            if pos in context._atlas_to_study:
                positions_to_analyze.append(pos)

        recommendations = []
        warnings_list = list(context.warnings)
        
        # Keep track of active case study IDs used
        active_cs_ids = {cs.case_study_id for cs in context.active_case_studies}
        excluded_cs_ids = []
        
        # Determine excluded case study IDs
        all_cs_summaries = context.active_case_studies + context.superseded_case_studies
        # We can query all case study IDs in the project
        from engine.case_study_repository import CaseStudyRepository
        cs_repo = CaseStudyRepository()
        for summary in cs_repo.list_case_studies(project, include_archived=True):
            cs_id = summary["case_study_id"]
            if cs_id not in active_cs_ids:
                excluded_cs_ids.append(cs_id)

        # 4. Generate, score, and annotate proposals
        all_proposals_dicts = []
        for atlas_pos in positions_to_analyze:
            study_pos = context._atlas_to_study[atlas_pos]
            residue = Residue(atlas_pos)
            
            # Generate proposals
            proposals = self.proposal_engine.generate_for_residue(residue)
            
            # Retrieve CaseStudy evidence for this position
            evidence_records = context.residue_evidence_by_atlas_position.get(atlas_pos, [])
            
            # Separate evidence categories
            sim_evs = []
            struct_evs = []
            exp_evs = []
            for ev in evidence_records:
                if ev.evidence_type.startswith("simulation_"):
                    sim_evs.append(ev)
                elif ev.evidence_type.startswith("structural_"):
                    struct_evs.append(ev)
                elif ev.evidence_type.startswith("experimental_"):
                    exp_evs.append(ev)

            global_ev = {
                "fvi": residue.fvi,
                "global_conservation": residue.global_conservation,
                "global_consensus": residue.global_consensus,
                "known_mutations": residue.known_mutations or []
            }
            family_ev = {
                "predicted_family": context.predicted_family,
                "family_consensus": residue.family_consensus
            }

            # Build position-level contradictory tags (evolutionary & structural)
            position_contradictory = []
            if residue.fvi is not None and residue.fvi <= 1:
                position_contradictory.append("evolutionary_conservation")
            
            # Check contact/hbond/energy disruptions
            has_contact = any(
                e.evidence_type == "simulation_contact" and e.value is not None and float(e.value) > 0.0
                for e in sim_evs
            )
            has_hbond = any(
                e.evidence_type == "simulation_hbond" and e.value is not None and float(e.value) > 0.0
                for e in sim_evs
            )
            has_energy = any(
                e.evidence_type == "simulation_energy" and e.value is not None
                for e in sim_evs
            )

            if has_contact:
                position_contradictory.append("ligand_contact_disruption")
            if has_hbond:
                position_contradictory.append("hydrogen_bond_disruption")
            if has_energy:
                position_contradictory.append("interaction_energy_disruption")

            # Score each proposal and assign qualitative tags
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
                        # Match mutant residue
                        if isinstance(km, dict) and km.get("mutant") == prop.to_residue:
                            is_known = True
                            break
                        elif isinstance(km, str) and len(km) > 0 and km[-1] == prop.to_residue:
                            is_known = True
                            break
                if is_known or "known_mutation" in scored_prop.sources:
                    supporting_tags.append("known_mutation_support")

                # 2. Family consensus support
                pred_fam = context.predicted_family
                if pred_fam in residue.family_consensus and residue.family_consensus[pred_fam] == prop.to_residue:
                    supporting_tags.append("family_consensus_support")

                # 3. Chemical conservative change
                if prop.is_conservative():
                    supporting_tags.append("conservative_substitution")

                # Make copy of contradictory tags for this proposal
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

                # Construct clean factual EvidenceExplanation organizing already-existing evidence
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

                if "family_consensus" in scored_prop.sources or (pred_fam in residue.family_consensus and residue.family_consensus[pred_fam] == prop.to_residue):
                    supporting_list.append("Family-consensus proposal")

                is_exact_published = False
                any_published_at_pos = False
                matched_km_exact = None
                matched_km_related = None
                
                known_list = residue.known_mutations
                if isinstance(known_list, str):
                    known_list = [k.strip() for k in known_list.split(",") if k.strip()]
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

                if sim_evs:
                    supporting_list.append("Simulation evidence available for the mapped residue")

                missing_list = []
                if not is_exact_published:
                    missing_list.append("exact proposed mutation lacks experimental validation")
                missing_list.append("no matched mutant-vs-reference simulation")

                if not struct_evs:
                    missing_list.append("no structural evidence")
                if not exp_evs:
                    missing_list.append("no experimental evidence")

                explanation = EvidenceExplanation(
                    supporting_evidence=supporting_list,
                    contradictory_evidence=contradictory_tags,
                    missing_evidence=missing_list,
                    final_interpretation=interpretation
                )

                # Resolve current residue in StudySequence
                curr_res = None
                norm_seq = project.primary_study_sequence.normalized_sequence
                
                if study_pos is None:
                    mutation_actionability = "unmapped"
                    project_mutation_label = None
                else:
                    idx = int(study_pos) - 1
                    if 0 <= idx < len(norm_seq):
                        curr_res = norm_seq[idx]
                    
                    if curr_res is None or curr_res not in "ACDEFGHIKLMNPQRSTVWY":
                        mutation_actionability = "invalid_mapping"
                        project_mutation_label = None
                    elif prop.to_residue == curr_res:
                        mutation_actionability = "already_present"
                        project_mutation_label = None
                    else:
                        mutation_actionability = "actionable"
                        project_mutation_label = f"{curr_res}{study_pos}{prop.to_residue}"

                # Append record
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
                    "simulation_evidence": [se.to_dict() for se in sim_evs],
                    "structural_evidence": [se.to_dict() for se in struct_evs],
                    "experimental_evidence": [se.to_dict() for se in exp_evs],
                    "supporting_evidence": supporting_tags,
                    "contradictory_evidence": contradictory_tags,
                    "active_case_study_ids": list(active_cs_ids),
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

        # 5. Rank proposals by position
        ranked_proposals = self.ranking_engine.rank_by_position(all_proposals_dicts)
        
        # Reformat recommendations into final structure
        for row in ranked_proposals:
            rec_dict = {
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
                "simulation_evidence": row["simulation_evidence"],
                "structural_evidence": row["structural_evidence"],
                "experimental_evidence": row["experimental_evidence"],
                "supporting_evidence": row["supporting_evidence"],
                "contradictory_evidence": row["contradictory_evidence"],
                "active_case_study_ids": row["active_case_study_ids"],
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
            }
            recommendations.append(rec_dict)

        return EngineeringRecommendationResult(
            project_id=project.project_id,
            study_id=context.study_id,
            predicted_family=context.predicted_family,
            family_classification_status=context.family_classification_status,
            recommendations=recommendations,
            positions_analyzed=positions_to_analyze,
            active_case_studies_used=list(active_cs_ids),
            excluded_case_studies=excluded_cs_ids,
            warnings=warnings_list
        )

    def build_structure_viewer_context(
        self,
        recommendation_dict: dict,
        case_study,
        study_sequence
    ) -> "StructureViewerContext":
        from pathlib import Path
        from engine.structure_viewer_context import StructureViewerContext
        from engine.reference_mapper import ReferenceMapper
        
        # 1. Base recommendation coordinate values
        atlas_position = recommendation_dict.get("atlas_position")
        atlas_reference_residue = recommendation_dict.get("atlas_reference_residue")
        atlas_mutation_label = recommendation_dict.get("atlas_mutation_label")
        study_position = recommendation_dict.get("study_position")
        study_current_residue = recommendation_dict.get("study_current_residue")
        project_mutation_label = recommendation_dict.get("project_mutation_label")
        mutation_actionability = recommendation_dict.get("mutation_actionability")

        proposed_residue = recommendation_dict.get("proposed_target_residue") or recommendation_dict.get("proposed_mutant")
        expected_notation = None
        if study_current_residue and study_position and proposed_residue:
            expected_notation = f"{study_current_residue}{study_position}{proposed_residue}"
            
        project_label = recommendation_dict.get("project_mutation_label")
        legacy_label = recommendation_dict.get("mutation_label")
        rec_label = project_label or legacy_label

        if rec_label and expected_notation:
            if rec_label != expected_notation:
                raise ValueError(f"Inconsistent mutation notation: '{rec_label}', expected '{expected_notation}'")
        mutation_notation = expected_notation

        # 2. Extract representative structure details
        rep_struct = case_study.representative_structure if hasattr(case_study, "representative_structure") else None
        
        if rep_struct is None:
            return StructureViewerContext(
                atlas_position=atlas_position,
                atlas_reference_residue=atlas_reference_residue,
                atlas_mutation_label=atlas_mutation_label,
                study_position=study_position,
                study_current_residue=study_current_residue,
                project_mutation_label=project_mutation_label,
                mutation_actionability=mutation_actionability,
                proposed_residue=proposed_residue,
                mutation_notation=mutation_notation,
                structure_mapping_status="unmapped",
                structure_available=False,
                target_highlight_ready=False,
                viewer_ready=False,
                viewer_message="No representative structure registered for this Case Study."
            )

        structure_relative_path = rep_struct.relative_path
        structure_type = rep_struct.structure_type
        protein_chain = rep_struct.protein_chain
        ligand_resname = rep_struct.ligand_resname
        ligand_chain = rep_struct.ligand_chain
        ligand_residue_number = rep_struct.ligand_residue_number

        # 3. Check file path long path suffix
        full_path = Path(case_study.case_study_path) / structure_relative_path
        
        def _win_long(p: Path) -> Path:
            import os
            if os.name == "nt":
                s = str(p.resolve())
                if not s.startswith("\\\\?\\"):
                    if s.startswith("\\\\"):
                        return Path("\\\\?\\UNC\\" + s[2:])
                    return Path("\\\\?\\" + s)
            return p

        full_path_safe = _win_long(full_path)
        
        # Instantiate mapper and check availability (delegating all parsing, CIF validation, and chain checks)
        mapper = ReferenceMapper()
        avail = mapper.check_structure_availability(str(full_path_safe), protein_chain)
        
        if not avail.viewer_ready:
            # Map structural status
            mapping_status = avail.status
            return StructureViewerContext(
                atlas_position=atlas_position,
                atlas_reference_residue=atlas_reference_residue,
                atlas_mutation_label=atlas_mutation_label,
                study_position=study_position,
                study_current_residue=study_current_residue,
                project_mutation_label=project_mutation_label,
                mutation_actionability=mutation_actionability,
                proposed_residue=proposed_residue,
                mutation_notation=mutation_notation,
                structure_relative_path=structure_relative_path,
                structure_type=structure_type,
                protein_chain=protein_chain,
                ligand_resname=ligand_resname,
                ligand_chain=ligand_chain,
                ligand_residue_number=ligand_residue_number,
                structure_mapping_status=mapping_status,
                structure_available=avail.structure_available,
                target_highlight_ready=False,
                viewer_ready=False,
                viewer_message=avail.message
            )

        # 4. Resolve Study position mapping (using the same cached mapper instance to avoid double parsing)
        mapping = mapper.map_study_to_structure(
            study_sequence=study_sequence,
            structure_path=str(full_path_safe),
            protein_chain=protein_chain,
            study_position=study_position
        )

        structure_mapping_status = mapping.mapping_status
        target_highlight_ready = mapping.can_highlight
        
        pdb_residue_number = mapping.pdb_residue_number
        pdb_insertion_code = mapping.pdb_insertion_code
        pdb_residue_name = mapping.pdb_residue_name

        viewer_message = "Structure ready for 3D display."
        if structure_mapping_status == "residue_mismatch":
            viewer_message = f"Structure loaded. Caution: target residue mismatch ({study_current_residue}{study_position} aligns to {pdb_residue_name} {pdb_residue_number})."
        elif not target_highlight_ready:
            viewer_message = f"Structure loaded, but target residue cannot be highlighted: {mapping.message}"

        return StructureViewerContext(
            atlas_position=atlas_position,
            atlas_reference_residue=atlas_reference_residue,
            atlas_mutation_label=atlas_mutation_label,
            study_position=study_position,
            study_current_residue=study_current_residue,
            project_mutation_label=project_mutation_label,
            mutation_actionability=mutation_actionability,
            proposed_residue=proposed_residue,
            mutation_notation=mutation_notation,
            structure_relative_path=structure_relative_path,
            structure_type=structure_type,
            protein_chain=protein_chain,
            pdb_residue_number=pdb_residue_number,
            pdb_insertion_code=pdb_insertion_code,
            pdb_residue_name=pdb_residue_name,
            ligand_resname=ligand_resname,
            ligand_chain=ligand_chain,
            ligand_residue_number=ligand_residue_number,
            structure_mapping_status=structure_mapping_status,
            structure_available=avail.structure_available,
            target_highlight_ready=target_highlight_ready,
            viewer_ready=avail.viewer_ready,
            viewer_message=viewer_message
        )
