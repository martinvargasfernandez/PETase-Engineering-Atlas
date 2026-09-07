import csv
from pathlib import Path
from Bio import SeqIO

atlas = Path("atlas_v3/petase_atlas_v3_master.tsv")
fasta = Path("sequences/evolution_natural/v2_hmm_validated.fasta")

out_table = Path("atlas_v3/petase_atlas_v3_bacterial_clean.tsv")
out_fasta = Path("atlas_v3/petase_atlas_v3_bacterial_clean.fasta")

exclude = {
    "A0A081CLD2",
    "A0A0A1SYU9",
    "A0A0D3IET5",
    "A0A0D3J3J8",
    "A0A0D3JPC9",
    "A0A0D3JWZ2",
    "A0A0D3JX57",
}

keep = set()
rows = []

with atlas.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    fieldnames = reader.fieldnames
    for row in reader:
        if row["accession"] not in exclude:
            rows.append(row)
            keep.add(row["tree_id"])

with out_table.open("w", newline="") as out:
    writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

records = [r for r in SeqIO.parse(fasta, "fasta") if r.id in keep]
SeqIO.write(records, out_fasta, "fasta")

print("Kept table rows:", len(rows))
print("Kept FASTA sequences:", len(records))
print("Table:", out_table)
print("FASTA:", out_fasta)
