import csv
from pathlib import Path

global_matrix = Path("atlas_v3/families/global_family_consensus_matrix.tsv")
fvi_file = Path("atlas_v3/families/family_variability_index.tsv")
mut_file = Path("metadata/engineering/known_mutations.tsv")
out_file = Path("atlas_v3/atlas_v3_master_position_table.tsv")

# -----------------------------
# Leer FVI
# -----------------------------

fvi = {}

with fvi_file.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        fvi[int(row["IsPETase_position"])] = row

# -----------------------------
# Leer mutaciones conocidas
# -----------------------------

mutations = {}

with mut_file.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        if row["Position"] in ("", "NA"):
            continue

        pos = int(row["Position"])
        mutations.setdefault(pos, []).append(
            f'{row["Variant"]}:{row["Mutation"]}'
        )

# -----------------------------
# Construir tabla maestra
# -----------------------------

with global_matrix.open() as f, out_file.open("w", newline="") as out:
    reader = csv.DictReader(f, delimiter="\t")

    family_consensus_cols = [
        c for c in reader.fieldnames
        if c.endswith("_consensus") and c not in ["Global_consensus"]
    ]

    fieldnames = [
        "IsPETase_position",
        "IsPETase_residue",
        "Global_consensus",
        "Global_conservation",
        "FVI",
        "Different_family_consensus",
        "Consensus_residues",
        "Major_consensus",
        "Known_mutations",
        "Mutation_evidence",
    ] + family_consensus_cols

    writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()

    for row in reader:
        if row["IsPETase_position"] == "NA":
            continue

        pos = int(row["IsPETase_position"])

        known = mutations.get(pos, [])

        out_row = {
            "IsPETase_position": pos,
            "IsPETase_residue": row["IsPETase_residue"],
            "Global_consensus": row["Global_consensus"],
            "Global_conservation": row["Global_conservation"],
            "FVI": fvi[pos]["FVI"],
            "Different_family_consensus": fvi[pos]["Different_family_consensus"],
            "Consensus_residues": fvi[pos]["Consensus_residues"],
            "Major_consensus": fvi[pos]["Major_consensus"],
            "Known_mutations": ",".join(known) if known else "NA",
            "Mutation_evidence": "YES" if known else "NO",
        }

        for col in family_consensus_cols:
            out_row[col] = row[col]

        writer.writerow(out_row)

print("Output:", out_file)
