class Mutation:
    """
    Scientific object representing a specific amino acid substitution.

    Example:
        R280A = position 280, from R to A
    """

    def __init__(
        self,
        position: int,
        from_residue: str = None,
        to_residue: str = None,
        wild_type: str = None,
        mutant: str = None,
        source: str = None,
        evidence: dict = None,
        score: float = 0,
        priority: str = "Low",
    ):
        self.position = int(position)

        self.from_residue = (from_residue or wild_type).upper()
        self.to_residue = (to_residue or mutant).upper()

        self.wild_type = self.from_residue
        self.mutant = self.to_residue

        self.source = source
        self.sources = [source] if source else []

        self.evidence = evidence or {}

        self.proposal_score = score
        self.proposal_priority = priority

        self.validate()

    def validate(self):
        valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")

        if self.from_residue not in valid_amino_acids:
            raise ValueError(f"Invalid wild-type residue: {self.from_residue}")

        if self.to_residue not in valid_amino_acids:
            raise ValueError(f"Invalid mutant residue: {self.to_residue}")

        if self.from_residue == self.to_residue:
            raise ValueError("Mutation must change the amino acid.")

    @property
    def label(self):
        return f"{self.from_residue}{self.position}{self.to_residue}"

    @property
    def candidate(self):
        return self.label

    @property
    def supporting_families(self):
        """
        Read-only compatibility property returning supporting protein families.
        """
        return self.evidence.get("supporting_families", [])

    @property
    def proposal_score_components(self):
        """
        Read-only compatibility property returning scoring components.
        """
        return self.evidence.get("proposal_score_components", {})

    def is_conservative(self):
        conservative_groups = [
            set("AVLIM"),
            set("FWY"),
            set("STNQ"),
            set("KRH"),
            set("DE"),
        ]

        for group in conservative_groups:
            if self.from_residue in group and self.to_residue in group:
                return True

        return False

    def chemical_change(self):
        if self.is_conservative():
            return "Conservative"

        return "Non-conservative"

    def add_source(self, source):
        if source and source not in self.sources:
            self.sources.append(source)

    def add_evidence(self, evidence):
        if evidence:
            self.evidence.update(evidence)

    def to_dict(self):
        return {
            "position": self.position,
            "from_residue": self.from_residue,
            "to_residue": self.to_residue,
            "wild_type": self.wild_type,
            "mutant": self.mutant,

            # Compatibility names
            "label": self.label,
            "mutation": self.label,
            "candidate": self.label,

            "source": self.source,
            "sources": self.sources,
            "evidence": self.evidence,
            "chemical_change": self.chemical_change(),
            "proposal_score": self.proposal_score,
            "proposal_priority": self.proposal_priority,
        }