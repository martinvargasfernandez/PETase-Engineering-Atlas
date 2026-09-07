import csv
from collections import Counter
from pathlib import Path

matrix = Path("atlas_v3/families/global_family_consensus_matrix.tsv")
out = Path("atlas_v3/families/family_variability_index.tsv")

with matrix.open() as f:

    reader = csv.DictReader(f, delimiter="\t")

    with out.open("w", newline="") as o:

        writer = csv.writer(o, delimiter="\t")

        writer.writerow([
            "IsPETase_position",
            "Residue",
            "Different_family_consensus",
            "Consensus_residues",
            "Major_consensus",
            "Major_count",
            "FVI"
        ])

        for row in reader:

            if row["IsPETase_position"] == "NA":
                continue

            consensi = []

            for key, value in row.items():

                if key.endswith("_consensus"):

                    if value not in ("", "NA"):
                        consensi.append(value)

            counts = Counter(consensi)

            residues = sorted(counts)

            major, n = counts.most_common(1)[0]

            fvi = len(residues) - 1

            writer.writerow([
                row["IsPETase_position"],
                row["IsPETase_residue"],
                len(residues),
                ",".join(residues),
                major,
                n,
                fvi
            ])

print("Output:", out)
