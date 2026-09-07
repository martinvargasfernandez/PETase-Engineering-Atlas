import json
import pathlib

def get_project_version() -> str:
    """
    Parses the central project version from VERSION.md.
    """
    path = pathlib.Path(__file__).parent.parent / "VERSION.md"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Version "):
                        return line.replace("Version ", "").strip()
        except Exception:
            pass
    return "1.0"

class SequenceAnalysisResult:
    """
    Scientific Entity: SequenceAnalysisResult

    Represents the complete integrated analysis output for one input StudySequence.
    Encapsulates sequence information, alignment coordinates, projected evidence,
    and family assignments.
    """

    def __init__(
        self,
        study_sequence,
        mapping_result,
        projected_sequence,
        family_classification,
        analysis_method: str = "standard_pipeline",
        function_first_hotspots: list = None
    ):
        # Validate input interfaces via duck typing
        if not hasattr(study_sequence, "study_id") or not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")
        if not hasattr(mapping_result, "alignment_score") or not hasattr(mapping_result, "identity_percent"):
            raise TypeError("mapping_result must implement the MappingResult interface.")
        if not hasattr(projected_sequence, "projected_residues") or not hasattr(projected_sequence, "to_table"):
            raise TypeError("projected_sequence must implement the ProjectedSequence interface.")
        if not hasattr(family_classification, "predicted_family") or not hasattr(family_classification, "classification_status"):
            raise TypeError("family_classification must implement the FamilyClassificationResult interface.")

        self._study_sequence = study_sequence
        self._mapping_result = mapping_result
        self._projected_sequence = projected_sequence
        self._family_classification = family_classification
        self._analysis_method = str(analysis_method)
        self._analysis_version = get_project_version()
        self._function_first_hotspots = function_first_hotspots if function_first_hotspots is not None else []

        # Build combined warnings list with stage labels
        combined_warnings = []
        
        # Sequence warnings
        for w in self._study_sequence.validation_warnings:
            msg = w["message"] if isinstance(w, dict) and "message" in w else str(w)
            combined_warnings.append({"stage": "sequence", "message": msg})
            
        # Mapping warnings
        for w in self._mapping_result.warnings:
            msg = w["message"] if isinstance(w, dict) and "message" in w else str(w)
            combined_warnings.append({"stage": "mapping", "message": msg})

        # Mapping quality warnings
        if hasattr(self._mapping_result, "mapping_quality_warnings"):
            for w in self._mapping_result.mapping_quality_warnings:
                combined_warnings.append({"stage": "mapping_quality", "message": w})

        # Projection warnings (de-duplicate identical messages from mapping)
        for w in self._projected_sequence.warnings:
            msg = w["message"] if isinstance(w, dict) and "message" in w else str(w)
            if not any(cw["stage"] == "mapping" and cw["message"] == msg for cw in combined_warnings):
                combined_warnings.append({"stage": "projection", "message": msg})

        # Family classification warnings
        for w in self._family_classification.warnings:
            msg = w["message"] if isinstance(w, dict) and "message" in w else str(w)
            combined_warnings.append({"stage": "family_classification", "message": msg})

        self._warnings = tuple(combined_warnings)

    @property
    def study_sequence(self):
        return self._study_sequence

    @property
    def study_id(self) -> str:
        return self._study_sequence.study_id

    @property
    def mapping_result(self):
        return self._mapping_result

    @property
    def projected_sequence(self):
        return self._projected_sequence

    @property
    def family_classification(self):
        return self._family_classification

    @property
    def analysis_method(self) -> str:
        return self._analysis_method

    @property
    def analysis_version(self) -> str:
        return self._analysis_version

    @property
    def function_first_hotspots(self) -> list:
        return self._function_first_hotspots

    @property
    def coordinate_system(self) -> str:
        return self._mapping_result.coordinate_system

    @property
    def sequence_hash(self) -> str:
        return self._study_sequence.sequence_hash

    @property
    def warnings(self) -> tuple:
        return self._warnings

    @property
    def classification_method(self) -> str:
        if hasattr(self._family_classification, "method"):
            return self._family_classification.method
        return "FamilyClassifier_v1"

    @property
    def query_sequence_length(self) -> int:
        return self._mapping_result.query_sequence_length

    @property
    def reference_sequence_length(self) -> int:
        return self._mapping_result.reference_sequence_length

    @property
    def aligned_query_residues(self) -> int:
        return self._mapping_result.aligned_query_residues

    @property
    def mapped_atlas_positions(self) -> int:
        return self._mapping_result.mapped_atlas_positions

    @property
    def sequence_identity(self) -> float:
        return self._mapping_result.sequence_identity

    @property
    def query_coverage(self) -> float:
        return self._mapping_result.query_coverage

    @property
    def reference_coverage(self) -> float:
        return self._mapping_result.reference_coverage

    @property
    def number_of_insertions(self) -> int:
        return self._mapping_result.number_of_insertions

    @property
    def number_of_deletions(self) -> int:
        return self._mapping_result.number_of_deletions

    @property
    def number_of_unmapped_query_residues(self) -> int:
        return self._mapping_result.number_of_unmapped_query_residues

    @property
    def number_of_unmapped_atlas_positions(self) -> int:
        return self._mapping_result.number_of_unmapped_atlas_positions

    @property
    def mapping_quality_warnings(self) -> tuple[str, ...]:
        return self._mapping_result.mapping_quality_warnings

    def describe(self) -> str:
        return (
            f"SequenceAnalysisResult for {self.study_id} | "
            f"Method: {self.analysis_method} (v{self.analysis_version}) | "
            f"Coordinate System: {self.coordinate_system} | "
            f"Predicted Family: {self.family_classification.predicted_family} | "
            f"Identity: {self.mapping_result.identity_percent:.2f}% | "
            f"Warnings: {len(self.warnings)}"
        )

    def to_table(self) -> list:
        return self._projected_sequence.to_table()

    def get_mutation_recommendations(
        self,
        excluded_atlas_positions: list = None,
        minimum_fvi: int = 1
    ) -> list:
        """
        Generate sequence-specific mutation recommendations expressed in query numbering.

        Recommendations are derived exclusively from global Atlas evidence (family
        variability, family/global consensus, known mutations, Atlas evidence score).
        No case-study, MD, or structural data is incorporated.

        Only query positions that are fully mapped (not insertions, not deletions,
        not unmapped) are eligible for recommendations.

        Parameters:
            excluded_atlas_positions : list of int, optional
                Atlas position IDs to exclude from recommendations (e.g.
                ``list(ATLAS_CATALYTIC_TRIAD)`` → [160, 206, 237], the canonical
                catalytic triad defined in ``engine.atlas_constants``).
            minimum_fvi : int
                Minimum Family Variability Index required for a position to be eligible.
                Default 1.

        Returns:
            list of SequenceMutationRecommendation, ranked by proposal_score descending,
            then atlas_evidence_score descending, then atlas_position ascending.
        """
        import math
        from engine.sequence_mutation_recommendation import SequenceMutationRecommendation
        from engine.candidate_discovery import CandidateDiscoveryEngine
        from engine.mapping_status import MappingStatus
        from engine.residue import Residue
        from engine.mutation_proposal_engine import MutationProposalEngine
        from engine.proposal_scoring import ProposalScoringEngine
        from engine.mutation_ranking import MutationRankingEngine
        from engine.proposal_generators.family_consensus_generator import FamilyConsensusGenerator
        from engine.proposal_generators.known_mutation_generator import KnownMutationGenerator

        def _clean(v):
            """Normalize numpy scalars and NaN to Python-native values."""
            if v is None:
                return None
            try:
                if isinstance(v, float) and math.isnan(v):
                    return None
            except TypeError:
                pass
            if hasattr(v, "item"):
                try:
                    return v.item()
                except (TypeError, ValueError):
                    pass
            return v

        # Build canonical pipeline components (no global state mutated)
        proposal_engine = MutationProposalEngine(
            generators=[
                FamilyConsensusGenerator(),
                KnownMutationGenerator(),
            ]
        )
        scoring_engine = ProposalScoringEngine()
        ranking_engine = MutationRankingEngine()

        # Discover eligible Atlas positions (respects min_fvi and explicit exclusions)
        discovery_engine = CandidateDiscoveryEngine(
            min_fvi=minimum_fvi,
            exclude_positions=excluded_atlas_positions,
        )
        candidate_atlas_positions = set(discovery_engine.get_positions())

        all_proposal_dicts = []

        for mr in self._mapping_result.mapped_residues:
            # Deletions have no query position — skip entirely
            if mr.mapping_status == MappingStatus.DELETION:
                continue
            # Insertions and unmapped residues have no Atlas position — skip
            if mr.atlas_position is None:
                continue
            # Only fully mapped query residues are eligible
            query_state = getattr(mr, "query_mapping_state", None)
            if query_state != "mapped":
                continue

            atlas_pos = mr.atlas_position.atlas_position_id

            # Apply FVI filter and exclusion list
            if atlas_pos not in candidate_atlas_positions:
                continue

            query_pos = mr.study_position
            query_res = mr.study_residue

            # Require a valid standard amino acid at this query position
            if not query_res or query_res not in "ACDEFGHIKLMNPQRSTVWY":
                continue

            residue = Residue(atlas_pos)
            proposals = proposal_engine.generate_for_residue(residue)

            global_ev = {
                "fvi": _clean(residue.fvi),
                "global_conservation": _clean(residue.global_conservation),
                "global_consensus": residue.global_consensus,
                "known_mutations": residue.known_mutations or [],
            }

            for prop in proposals:
                scoring_engine.score(prop, residue)

                # Omit proposals where the target AA equals the current query residue (no-op)
                if prop.to_residue == query_res:
                    continue

                # Extract known mutation evidence string if this is a known-mutation proposal
                known_mut_evidence = None
                if "known_mutation" in prop.sources:
                    km_detail = prop.evidence.get("known_mutation")
                    known_mut_evidence = str(km_detail) if km_detail else None

                all_proposal_dicts.append({
                    "position": atlas_pos,
                    "study_position": query_pos,
                    "query_residue": query_res,
                    "atlas_reference_residue": prop.from_residue,
                    "proposed_mutant": prop.to_residue,
                    "mutation_label": prop.label,
                    "candidate": prop.label,
                    "query_notation": f"{query_res}{query_pos}{prop.to_residue}",
                    "atlas_notation": prop.label,
                    "proposal_score": prop.proposal_score,
                    "proposal_priority": prop.proposal_priority,
                    "atlas_evidence_score": _clean(residue.atlas_evidence_score),
                    "sources": list(prop.sources),
                    "global_evidence": global_ev,
                    "supporting_families": list(prop.evidence.get("supporting_families", [])),
                    "known_mutation_evidence": known_mut_evidence,
                })

        # Rank proposals: best per position, then overall by score DESC
        ranked = ranking_engine.rank_by_position(all_proposal_dicts)

        results = []
        for row in ranked:
            query_pos_row = row["study_position"]
            query_res_row = row["query_residue"]

            # Build alternatives in query notation; remove no-op and deduplicate
            raw_alts = row.get("alternative_candidates_with_sources", [])
            seen_mutants = set()
            filtered_alts = []
            for alt in raw_alts:
                cand = alt.get("candidate", "")
                if len(cand) >= 1:
                    mutant_aa = cand[-1]
                    if mutant_aa == query_res_row:
                        continue  # no-op in query numbering
                    if mutant_aa in seen_mutants:
                        continue  # deduplicate
                    seen_mutants.add(mutant_aa)
                    filtered_alts.append({
                        "query_notation": f"{query_res_row}{query_pos_row}{mutant_aa}",
                        "atlas_notation": cand,
                        "proposed_mutant": mutant_aa,
                        "sources": alt.get("sources", []),
                        "proposal_score": alt.get("proposal_score", 0),
                        "proposal_priority": alt.get("proposal_priority", "Low"),
                    })

            rec = SequenceMutationRecommendation(
                study_id=self.study_id,
                query_position=query_pos_row,
                query_residue=query_res_row,
                atlas_position=row["position"],
                atlas_reference_residue=row["atlas_reference_residue"],
                proposed_mutant=row["proposed_mutant"],
                query_notation=row["query_notation"],
                atlas_notation=row["atlas_notation"],
                proposal_score=row["proposal_score"],
                proposal_priority=row["proposal_priority"],
                sources=row.get("sources", []),
                global_evidence=row["global_evidence"],
                supporting_families=row.get("supporting_families", []),
                known_mutation_evidence=row.get("known_mutation_evidence"),
                alternatives=filtered_alts,
            )
            results.append(rec)

        return results

    def mutation_recommendations_to_table(
        self,
        excluded_atlas_positions: list = None,
        minimum_fvi: int = 1
    ) -> list:
        """
        Return mutation recommendations as a list of plain dicts for tabular export.

        Equivalent to calling get_mutation_recommendations() and converting each
        SequenceMutationRecommendation to its to_dict() representation.

        Parameters:
            excluded_atlas_positions : list of int, optional
            minimum_fvi : int

        Returns:
            list of dict, one per recommended position.
        """
        recs = self.get_mutation_recommendations(
            excluded_atlas_positions=excluded_atlas_positions,
            minimum_fvi=minimum_fvi,
        )
        return [r.to_dict() for r in recs]

    def to_dict(
        self,
        include_residue_table: bool = False,
        include_recommendations: bool = False,
        excluded_atlas_positions: list = None,
        minimum_fvi: int = 1
    ) -> dict:
        data = {
            "entity": "SequenceAnalysisResult",
            "schema_version": 1,
            "study_id": self.study_id,
            "coordinate_system": self.coordinate_system,
            "sequence_hash": self.sequence_hash,
            "analysis_method": self.analysis_method,
            "analysis_version": self.analysis_version,
            "classification_method": self.classification_method,
            "study_sequence": {
                "study_id": self._study_sequence.study_id,
                "name": self._study_sequence.name,
                "length": self._study_sequence.length,
                "sequence_hash": self._study_sequence.sequence_hash
            },
            "mapping": {
                "alignment_score": self._mapping_result.alignment_score,
                "identity_percent": self._mapping_result.identity_percent,
                "study_coverage_percent": self._mapping_result.study_coverage_percent,
                "reference_coverage_percent": self._mapping_result.reference_coverage_percent,
                "exact_matches": self._mapping_result.exact_matches,
                "substitutions": self._mapping_result.substitutions,
                "insertions": self._mapping_result.insertions,
                "deletions": self._mapping_result.deletions,
                "optimal_alignment_count": self._mapping_result.optimal_alignment_count,
                "alignment_is_ambiguous": self._mapping_result.alignment_is_ambiguous
            },
            "mapping_quality": {
                "query_sequence_length": self.query_sequence_length,
                "reference_sequence_length": self.reference_sequence_length,
                "aligned_query_residues": self.aligned_query_residues,
                "mapped_atlas_positions": self.mapped_atlas_positions,
                "sequence_identity": self.sequence_identity,
                "query_coverage": self.query_coverage,
                "reference_coverage": self.reference_coverage,
                "number_of_insertions": self.number_of_insertions,
                "number_of_deletions": self.number_of_deletions,
                "number_of_unmapped_query_residues": self.number_of_unmapped_query_residues,
                "number_of_unmapped_atlas_positions": self.number_of_unmapped_atlas_positions,
                "mapping_quality_warnings": list(self.mapping_quality_warnings),
            },
            "family_classification": {
                "predicted_family": self._family_classification.predicted_family,
                "classification_status": self._family_classification.classification_status,
                "confidence_status": self._family_classification.confidence_status,
                "best_score": self._family_classification.best_score,
                "second_best_score": self._family_classification.second_best_score,
                "score_margin": self._family_classification.score_margin
            },
            "warnings": [dict(w) for w in self.warnings]
        }
        if include_residue_table:
            data["residue_table"] = self.to_table()
        if include_recommendations:
            data["mutation_recommendations"] = self.mutation_recommendations_to_table(
                excluded_atlas_positions=excluded_atlas_positions,
                minimum_fvi=minimum_fvi,
            )
        return data

    def to_json(
        self,
        include_recommendations: bool = False,
        excluded_atlas_positions: list = None,
        minimum_fvi: int = 1
    ) -> str:
        return json.dumps(
            self.to_dict(
                include_residue_table=False,
                include_recommendations=include_recommendations,
                excluded_atlas_positions=excluded_atlas_positions,
                minimum_fvi=minimum_fvi,
            ),
            sort_keys=True
        )
