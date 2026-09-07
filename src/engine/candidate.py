import math


def clean_value(value):
    """
    Convert pandas/numpy values into clean Python values.
    """

    if value is None:
        return None

    try:
        if isinstance(value, float) and math.isnan(value):
            return None
    except TypeError:
        pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


class Candidate:
    """
    Scientific object representing a proposed mutation candidate.
    """

    def __init__(self, residue, mutation):
        self.residue = residue
        self.mutation = mutation
        self.validate()

    def validate(self):
        if self.residue.position != self.mutation.position:
            raise ValueError(
                "Residue position and mutation position do not match."
            )

        if self.residue.reference_residue != self.mutation.from_residue:
            raise ValueError(
                f"Mutation starts from {self.mutation.from_residue}, "
                f"but Atlas reference residue is {self.residue.reference_residue}."
            )

    @property
    def label(self):
        return self.mutation.label

    @property
    def supporting_families(self):
        """
        Read-only compatibility property delegating to the mutation.
        """
        return self.mutation.supporting_families

    @property
    def proposal_score_components(self):
        """
        Read-only compatibility property delegating to the mutation.
        """
        return self.mutation.proposal_score_components

    @property
    def proposal_score(self):
        """
        Read-only compatibility property delegating to the mutation.
        """
        return self.mutation.proposal_score

    @property
    def proposal_priority(self):
        """
        Read-only compatibility property delegating to the mutation.
        """
        return self.mutation.proposal_priority

    def to_dict(self):
        known_mutations = clean_value(self.residue.known_mutations)

        if known_mutations is None:
            known_mutations = []

        return {
            "candidate": self.label,
            "position": int(self.residue.position),
            "from_residue": self.mutation.from_residue,
            "to_residue": self.mutation.to_residue,
            "chemical_change": self.mutation.chemical_change(),
            "atlas_evidence_score": clean_value(self.residue.atlas_evidence_score),
            "atlas_priority": clean_value(self.residue.priority),
            "global_conservation": clean_value(self.residue.global_conservation),
            "fvi": clean_value(self.residue.fvi),
            "known_mutations": known_mutations,
        }