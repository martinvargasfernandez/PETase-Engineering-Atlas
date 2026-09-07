import csv
from pathlib import Path

master = Path("atlas_v3/atlas_v3_master_position_table.tsv")
out = Path("atlas_v3/evolutionary_candidates.tsv")

from engine.atlas_constants import ATLAS_CATALYTIC_TRIAD

with master.open() as f, out.open("w", newline="") as o:

    reader = csv.DictReader(f, delimiter="\t")

    writer = csv.DictWriter(
        o,
        fieldnames=reader.fieldnames,
        delimiter="\t"
    )

    writer.writeheader()

    kept = 0

    for row in reader:

        pos = int(row["IsPETase_position"])

        if pos in ATLAS_CATALYTIC_TRIAD:
            continue

        if int(row["FVI"]) >= 3:
            writer.writerow(row)
            kept += 1

print("Candidates:", kept)
print("Output:", out)
