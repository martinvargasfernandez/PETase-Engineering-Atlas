from engine import families


class FamilyEngine:
    """
    Provides family-level summaries and consensus exploration.
    """

    def __init__(self):
        self.summary = families.get_family_summary()
        self.consensus_matrix = families.load_global_family_consensus_matrix()
        self.variability = families.load_family_variability_index()

    def get_families(self):
        if self.summary.empty:
            return []

        return sorted(self.summary["family_name"].dropna().unique().tolist())

    def get_family_summary(self):
        return self.summary

    def get_consensus_matrix(self):
        return self.consensus_matrix

    def get_variability_table(self):
        return self.variability

    def get_family_positions(self, family_name: str):
        df = self.consensus_matrix.copy()

        consensus_col = f"{family_name}_consensus"
        conservation_col = f"{family_name}_conservation"
        nseq_col = f"{family_name}_nseq"

        if consensus_col not in df.columns:
            return df.iloc[0:0]

        columns = [
            "Alignment_position",
            "IsPETase_position",
            "IsPETase_residue",
            "Global_consensus",
            "Global_conservation",
            consensus_col,
            conservation_col,
            nseq_col,
        ]

        columns = [col for col in columns if col in df.columns]

        result = df[columns].copy()

        result = result.rename(
            columns={
                "IsPETase_position": "position",
                "IsPETase_residue": "reference_residue",
                "Global_consensus": "global_consensus",
                "Global_conservation": "global_conservation",
                consensus_col: "family_consensus",
                conservation_col: "family_conservation",
                nseq_col: "family_nseq",
            }
        )

        return result

    def get_position_family_consensus(self, position: int):
        df = self.consensus_matrix.copy()

        if "IsPETase_position" not in df.columns:
            return {}

        row = df[df["IsPETase_position"] == int(position)]

        if row.empty:
            return {}

        row = row.iloc[0].to_dict()
        result = {}

        for family in self.get_families():
            consensus_col = f"{family}_consensus"
            conservation_col = f"{family}_conservation"
            nseq_col = f"{family}_nseq"

            result[family] = {
                "consensus": row.get(consensus_col),
                "conservation": row.get(conservation_col),
                "nseq": row.get(nseq_col),
            }

        return result