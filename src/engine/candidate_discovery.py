from engine import families
from engine.atlas_constants import ATLAS_CATALYTIC_TRIAD


class CandidateDiscoveryEngine:
    """
    Discovers Atlas positions worth analyzing for mutation proposal.

    Current version:
    - uses FVI from the family variability table
    - enforces ATLAS_CATALYTIC_TRIAD (160, 206, 237) as an engine-level invariant
    - caller-supplied exclude_positions are additive to ATLAS_CATALYTIC_TRIAD
    """

    def __init__(
        self,
        min_fvi=1,
        exclude_positions=None,
    ):
        self.min_fvi = min_fvi
        caller_exclusions = set(exclude_positions or [])
        self.exclude_positions = set(ATLAS_CATALYTIC_TRIAD) | caller_exclusions
        self.variability_table = families.load_family_variability_index()

    def discover_positions(self):
        df = self.variability_table.copy()

        position_col = "IsPETase_position"
        fvi_col = "FVI"

        required = [position_col, fvi_col]

        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df = df.dropna(subset=[position_col])

        df = df[df[fvi_col] >= self.min_fvi]

        df = df[~df[position_col].isin(self.exclude_positions)]

        df = df.sort_values(
            [fvi_col, position_col],
            ascending=[False, True]
        )

        return df

    def get_positions(self, limit=None):
        df = self.discover_positions()

        positions = df["IsPETase_position"].astype(int).tolist()

        if limit:
            positions = positions[:limit]

        return positions

    def to_table(self, limit=None):
        df = self.discover_positions()

        if limit:
            df = df.head(limit)

        return df