from engine.residue import Residue
from engine.case_study_engine import CaseStudyEngine
from engine.candidate_discovery import CandidateDiscoveryEngine

from engine.mutation_proposal_engine import MutationProposalEngine
from engine.proposal_scoring import ProposalScoringEngine
from engine.engineering_report import EngineeringReport

from engine.proposal_generators.family_consensus_generator import (
    FamilyConsensusGenerator,
)
from engine.proposal_generators.known_mutation_generator import (
    KnownMutationGenerator,
)


class EngineeringWorkspace:
    """
    Main scientific workflow of the PETase Engineering Atlas.
    """

    def __init__(
        self,
        case_study_name=None,
        min_fvi=1,
        exclude_positions=None,
    ):

        self.case_study_name = case_study_name

        self.case_engine = CaseStudyEngine()

        self.discovery_engine = CandidateDiscoveryEngine(
            min_fvi=min_fvi,
            exclude_positions=exclude_positions,
        )

        self.proposal_engine = MutationProposalEngine(
            generators=[
                FamilyConsensusGenerator(),
                KnownMutationGenerator(),
            ]
        )

        self.scoring_engine = ProposalScoringEngine()

    def discover_positions(self, limit=50):
        return self.discovery_engine.get_positions(limit=limit)

    def analyze_position(self, position):

        residue = Residue(position)

        proposals = self.proposal_engine.generate_for_residue(residue)

        scored = []

        for proposal in proposals:
            scored.append(
                self.scoring_engine.score(
                    mutation=proposal,
                    residue=residue,
                )
            )

        return EngineeringReport(
            residue=residue,
            proposals=scored,
        )

    def analyze_positions(self, positions):
        return [
            self.analyze_position(position)
            for position in positions
        ]

    def run(self, limit_positions=50):

        positions = self.discover_positions(limit_positions)

        reports = self.analyze_positions(positions)

        return reports