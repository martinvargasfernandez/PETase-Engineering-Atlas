class MutationProposalEngine:
    def __init__(self, generators_or_residue=None, generators=None):
        from engine.residue import Residue
        
        args = generators if generators is not None else generators_or_residue
        if isinstance(args, Residue):
            self.residue = args
            from engine.proposal_generators.family_consensus_generator import FamilyConsensusGenerator
            from engine.proposal_generators.known_mutation_generator import KnownMutationGenerator
            self.generators = [
                FamilyConsensusGenerator(),
                KnownMutationGenerator(),
            ]
        else:
            self.residue = None
            self.generators = args

    def generate_for_residue(self, residue):
        merged = {}

        for generator in self.generators:
            proposals = generator.generate(residue)

            for proposal in proposals:
                key = (proposal.position, proposal.wild_type, proposal.mutant)

                if key not in merged:
                    merged[key] = proposal
                    merged[key].sources = [proposal.source]
                else:
                    if proposal.source not in merged[key].sources:
                        merged[key].sources.append(proposal.source)

                    if hasattr(merged[key], "evidence") and hasattr(proposal, "evidence"):
                        merged[key].evidence.update(proposal.evidence)

        return list(merged.values())

    def generate(self, residues=None):
        if residues is not None:
            from engine.residue import Residue
            if isinstance(residues, Residue):
                return self.generate_for_residue(residues)
                
            all_proposals = []
            for residue in residues:
                all_proposals.extend(self.generate_for_residue(residue))
            return all_proposals
            
        if self.residue is not None:
            return self.generate_for_residue(self.residue)
            
        raise ValueError("No residues supplied and no default residue initialized in the engine.")

    def get_family_supported_residues(self):
        if not hasattr(self, "residue") or self.residue is None:
            raise ValueError("Engine must be initialized with a residue to call get_family_supported_residues().")
            
        import math
        
        supported = set()
        for aa in self.residue.family_consensus.values():
            if aa is None:
                continue
            
            try:
                if isinstance(aa, float) and math.isnan(aa):
                    continue
            except TypeError:
                pass
                
            aa_str = str(aa).strip().upper()
            if len(aa_str) == 1 and aa_str in "ACDEFGHIKLMNPQRSTVWY" and aa_str != self.residue.reference_residue:
                supported.add(aa_str)
                
        return sorted(list(supported))

    def _clean_value(self, value):
        import math

        if value is None:
            return None

        if isinstance(value, dict):
            return {
                self._clean_value(key): self._clean_value(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [self._clean_value(item) for item in value]

        try:
            if isinstance(value, float) and math.isnan(value):
                return None
        except TypeError:
            pass

        if hasattr(value, "item"):
            try:
                return value.item()
            except (TypeError, ValueError):
                pass

        return value

    def to_table(self):
        if not hasattr(self, "residue") or self.residue is None:
            raise ValueError("Engine must be initialized with a residue to call to_table().")
            
        import math
        from engine.proposal_scoring import ProposalScoringEngine
        scoring_engine = ProposalScoringEngine()
        
        proposals = self.generate(residues=None)
        rows = []
        for proposal in proposals:
            scoring_engine.score(proposal, self.residue)
            
            row = proposal.to_dict()
            
            # Add or rename specific fields expected by templates/callers
            row["proposal_source"] = proposal.source
            row["global_conservation"] = self.residue.global_conservation
            row["fvi"] = self.residue.fvi
            row["atlas_evidence_score"] = self.residue.atlas_evidence_score

            # Promote nested evidence fields to top-level columns for UI and TSV export
            row["supporting_families"] = list(proposal.evidence.get("supporting_families", []))
            row["proposal_score_components"] = proposal.evidence.get("proposal_score_components", {})
            row["atlas_priority"] = self.residue.priority
            
            known = self.residue.known_mutations
            if known is None or (isinstance(known, float) and math.isnan(known)):
                row["known_mutations"] = ""
            else:
                row["known_mutations"] = str(known)
                
            # Clean recursively using the approved _clean_value
            clean_row = self._clean_value(row)
            rows.append(clean_row)
            
        return rows