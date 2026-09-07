import csv
from pathlib import Path
from Bio import SeqIO

atlas = Path("atlas_v3/petase_atlas_v3_master.tsv")
taxonomy = Path("atlas_v3/petase_atlas_v3_taxonomy.tsv")
fasta = Path("sequences/evolution_natural/v2_hmm_validated.fasta")

out_table = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean.tsv")
out_fasta = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean.fasta")

tax = {}
with taxonomy.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    for r in reader:
        tax[r["Entry"]] = r

keep_acc = set()

with atlas.open() as f, out_table.open("w", newline="") as out:
    reader = csv.DictReader(f, delimiter="\t")
    fieldnames = reader.fieldnames + ["taxonomic_lineage", "taxon_domain"]
    writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()

    for row in reader:
        acc = row["accession"]
        lineage = tax.get(acc, {}).get("Taxonomic lineage", "")

        if "Bacteria (domain)" in lineage:
            row["taxonomic_lineage"] = lineage
            row["taxon_domain"] = "Bacteria"
            writer.writerow(row)
            keep_acc.add(acc)

records = []
for rec in SeqIO.parse(fasta, "fasta"):
    acc = rec.id.split("|")[1] if "|" in rec.id else rec.id
    if acc in keep_acc:
        records.append(rec)

SeqIO.write(records, out_fasta, "fasta")

print("Bacterial entries:", len(keep_acc))
print("FASTA sequences:", len(records))
print("Table:", out_table)
print("FASTA:", out_fasta)
