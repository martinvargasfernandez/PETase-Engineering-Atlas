import re

from engine.residue import Residue
from engine.family_engine import FamilyEngine
from engine.case_study_engine import CaseStudyEngine
from engine.mutation_proposal_engine import MutationProposalEngine
from engine.proposal_scoring import ProposalScoringEngine

from engine.proposal_generators.family_consensus_generator import (
    FamilyConsensusGenerator,
)
from engine.proposal_generators.known_mutation_generator import (
    KnownMutationGenerator,
)


class ResidueContext:
    """
    Complete scientific context for one IsPETase reference position.
    """

    def __init__(
        self,
        residue,
        atlas_evidence,
        family_evidence,
        engineering_evidence,
        known_mutations,
        case_studies,
    ):
        self.residue = residue
        self.atlas_evidence = atlas_evidence
        self.family_evidence = family_evidence
        self.engineering_evidence = engineering_evidence
        self.known_mutations = known_mutations
        self.case_studies = case_studies

    def to_dict(self):
        return {
            "residue": {
                "position": self.residue.position,
                "reference_residue": self.residue.reference_residue,
            },
            "atlas_evidence": self.atlas_evidence,
            "family_evidence": self.family_evidence,
            "engineering_evidence": self.engineering_evidence,
            "known_mutations": self.known_mutations,
            "case_studies": self.case_studies,
        }


class KnowledgeGraphEngine:
    """
    Scientific aggregation engine for residue-centered Atlas evidence.

    This engine does not compute the Atlas Evidence Score.
    It only aggregates existing evidence.
    """

    def __init__(self):
        self.family_engine = FamilyEngine()
        self.case_study_engine = CaseStudyEngine()

        self.proposal_engine = MutationProposalEngine(
            generators=[
                FamilyConsensusGenerator(),
                KnownMutationGenerator(),
            ]
        )

        self.scoring_engine = ProposalScoringEngine()

    def get_residue_context(self, position):
        residue = Residue(int(position))

        atlas_evidence = self._get_atlas_evidence(residue)
        family_evidence = self._get_family_evidence(residue)
        engineering_evidence = self._get_engineering_evidence(residue)
        known_mutations = self._parse_known_mutations(residue.known_mutations)
        case_studies = self._get_case_studies(residue)

        return ResidueContext(
            residue=residue,
            atlas_evidence=atlas_evidence,
            family_evidence=family_evidence,
            engineering_evidence=engineering_evidence,
            known_mutations=known_mutations,
            case_studies=case_studies,
        )

    def _get_atlas_evidence(self, residue):
        return {
            "atlas_evidence_score": residue.atlas_evidence_score,
            "max_score": residue.max_score,
            "priority": residue.priority,
            "interpretation": residue.interpretation,
            "global_consensus": residue.global_consensus,
            "global_conservation": residue.global_conservation,
            "fvi": residue.fvi,
            "score_components": residue.score_components,
        }

    def _get_family_evidence(self, residue):
        return self.family_engine.get_position_family_consensus(
            residue.position
        )

    def _get_engineering_evidence(self, residue):
        proposals = self.proposal_engine.generate_for_residue(residue)

        scored = []

        for proposal in proposals:
            scored_proposal = self.scoring_engine.score(
                mutation=proposal,
                residue=residue,
            )

            scored.append(scored_proposal.to_dict())

        scored = sorted(
            scored,
            key=lambda row: row.get("proposal_score", 0),
            reverse=True,
        )

        return {
            "best_proposal": scored[0] if scored else None,
            "alternative_proposals": scored[1:] if len(scored) > 1 else [],
            "all_proposals": scored,
        }

    def _parse_known_mutations(self, known_mutations):
        if known_mutations is None:
            return []

        text = str(known_mutations).strip()

        if text == "" or text.lower() in {"nan", "none", "null", "na", "n/a", "-"}:
            return []

        raw_items = re.split(r"[;,|]", text)

        parsed = []

        for item in raw_items:
            item = item.strip()

            if not item:
                continue

            if ":" in item:
                source, mutation = item.split(":", 1)

                parsed.append(
                    {
                        "source": source.strip(),
                        "mutation": mutation.strip(),
                    }
                )

            else:
                parsed.append(
                    {
                        "source": None,
                        "mutation": item,
                    }
                )

        return parsed

    def _get_case_studies(self, residue):
        case_studies = []

        for name in ["BhrPETase", "TurboPETase", "ICCG", "LCC"]:
            context = self.case_study_engine.get_residue_context(
                name,
                residue.position,
            )

            case_studies.append(
                {
                    "case_study": name,
                    "evidence": context.get("evidence", {}) if context else {},
                    "available": bool(context and context.get("evidence")),
                }
            )

        return case_studies
