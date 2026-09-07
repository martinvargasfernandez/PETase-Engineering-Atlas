import math

from engine.mutation import Mutation


def is_missing(value):
    if value is None:
        return True

    try:
        if isinstance(value, float) and math.isnan(value):
            return True
    except TypeError:
        pass

    return False


class FamilyConsensusGenerator:
    """
    Generates mutation proposals from family consensus residues.
    """

    name = "family_consensus"

    def generate(self, residue):
        proposals = []
        seen = set()

        family_consensus = residue.family_consensus

        if not family_consensus:
            return proposals

        for family, aa in family_consensus.items():

            if is_missing(aa):
                continue

            aa = str(aa).strip().upper()

            if len(aa) != 1:
                continue

            if aa == residue.reference_residue:
                continue

            if aa in seen:
                continue

            seen.add(aa)

            proposals.append(
                Mutation(
                    position=residue.position,
                    wild_type=residue.reference_residue,
                    mutant=aa,
                    source=self.name,
                    evidence={
                        "supporting_families": [family],
                    },
                )
            )

        return proposals