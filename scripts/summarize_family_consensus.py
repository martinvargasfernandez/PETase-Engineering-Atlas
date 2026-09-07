from pathlib import Path
from Bio import AlignIO
import csv

cons_dir = Path("atlas_v3/families/consensus")
out = Path("atlas_v3/families/family_consensus_summary.tsv")

rows = []

for aln_file in sorted(cons_dir.glob("*_mafft.fasta")):
    family = aln_file.name.replace("_mafft.fasta", "").replace("_", "-")
    aln = AlignIO.read(aln_file, "fasta")
    rows.append([family, len(aln), aln.get_alignment_length()])

with out.open("w", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["Family", "Sequences", "Alignment_length"])
    writer.writerows(rows)

print("Output:", out)
