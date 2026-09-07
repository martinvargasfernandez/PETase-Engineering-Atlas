import csv
from pathlib import Path

atlas = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean.tsv")
neighbors = Path("atlas_v3/reference_neighbors_taxclean.tsv")
out = Path("atlas_v3/families/petase_atlas_v3_family_assignments.tsv")

ispetase_like = {"A0A0K8P6T7"}
lcc_like = {"G9BY57"}

with neighbors.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        if row["reference"] == "IsPETase" and float(row["distance"]) <= 0.90:
            ispetase_like.add(row["neighbor_accession"])
        if row["reference"] == "LCC" and float(row["distance"]) <= 0.90:
            lcc_like.add(row["neighbor_accession"])

def assign_family(row):
    acc = row["accession"]
    genus = row["genus"]

    if acc in ispetase_like:
        return "FAM01", "IsPETase-like"

    if acc in lcc_like:
        return "FAM02", "LCC-like"

    if genus == "Thermobifida":
        return "FAM03", "Thermobifida-like"

    if genus == "Actinomadura":
        return "FAM04", "Actinomadura-like"

    if genus == "Nocardiopsis":
        return "FAM05", "Nocardiopsis-like"

    if genus == "Amycolatopsis":
        return "FAM06", "Amycolatopsis-like"

    if genus == "Microbispora":
        return "FAM07", "Microbispora-like"

    if genus == "Streptomyces":
        return "FAM08", "Streptomyces-like"

    return "FAM09", "Other_bacterial"

with atlas.open() as f, out.open("w", newline="") as o:
    reader = csv.DictReader(f, delimiter="\t")
    fieldnames = reader.fieldnames + ["family_id", "family_name"]
    writer = csv.DictWriter(o, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()

    for row in reader:
        fid, fname = assign_family(row)
        row["family_id"] = fid
        row["family_name"] = fname
        writer.writerow(row)

print("Output:", out)
