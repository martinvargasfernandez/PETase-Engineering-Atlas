from Bio import AlignIO
from collections import Counter
from pathlib import Path
import csv

alignment = "atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean_mafft.fasta"
outfile = Path("atlas_v3/atlas_v3_taxclean_IsPETase_reference_table.tsv")
AA = set("ACDEFGHIKLMNPQRSTVWY")

aln = AlignIO.read(alignment, "fasta")

target = None
for rec in aln:
    if "A0A0K8P6T7" in rec.id:
        target = rec
        break

if target is None:
    raise SystemExit("IsPETase not found")

pos = 0

with outfile.open("w", newline="") as out:
    writer = csv.writer(out, delimiter="\t")
    writer.writerow(["IsPETase_position","Residue","Alignment_position","Consensus","Conservation_percent","Unique_aminoacids","Counts"])

    for aln_pos, aa in enumerate(str(target.seq), start=1):
        if aa == "-":
            continue
        pos += 1
        column = aln[:, aln_pos - 1]
        residues = [x for x in column if x in AA]
        counts = Counter(residues)
        consensus, n = counts.most_common(1)[0]
        conservation = round(100 * n / len(residues), 2)
        counts_string = ",".join(f"{k}:{counts[k]}" for k in sorted(counts))
        writer.writerow([pos, aa, aln_pos, consensus, conservation, len(counts), counts_string])

print("Output:", outfile)
print("Mapped residues:", pos)
