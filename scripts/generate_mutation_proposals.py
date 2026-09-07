import pandas as pd

from engine.residue import Residue
from engine.mutation_proposal_engine import MutationProposalEngine


POSITIONS = [132, 138, 176, 177, 238, 243]

OUTPUT = "results/mutation_proposals.tsv"


def main():
    all_rows = []

    for position in POSITIONS:
        try:
            residue = Residue(position)
            engine = MutationProposalEngine(residue)
            all_rows.extend(engine.to_table())

        except ValueError as error:
            print(f"Skipping position {position}: {error}")

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT, sep="\t", index=False)

    print(f"Saved: {OUTPUT}")
    print(df)


if __name__ == "__main__":
    main()