from Bio import AlignIO
import csv
from pathlib import Path

alignment = "alignments/pet_family_bacterial_mafft_trim50.fasta"
conservation = "conservation/pet_family_conservation.tsv"
outfile = Path("conservation/pet_family_conservation_mapped_IsPETase.tsv")

aln = AlignIO.read(alignment, "fasta")

target = None
for rec in aln:
    if "A0A0K8P6T7" in rec.id:
        target = rec
        break

if target is None:
    raise SystemExit("ERROR: IsPETase A0A0K8P6T7 not found")

# mapa alineamiento -> posición IsPETase
isp_pos = 0
align_to_isp = {}

for i, aa in enumerate(str(target.seq), start=1):
    if aa != "-":
        isp_pos += 1
        align_to_isp[i] = isp_pos
    else:
        align_to_isp[i] = "NA"

with open(conservation) as f, outfile.open("w", newline="") as out:
    reader = csv.DictReader(f, delimiter="\t")
    fieldnames = ["Alignment_position", "IsPETase_position", "IsPETase_residue"] + [
        x for x in reader.fieldnames if x != "Alignment_position"
    ]
    writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()

    for row in reader:
        aln_pos = int(row["Alignment_position"])
        isp_position = align_to_isp.get(aln_pos, "NA")
        isp_residue = str(target.seq)[aln_pos - 1]

        writer.writerow({
            "Alignment_position": aln_pos,
            "IsPETase_position": isp_position,
            "IsPETase_residue": isp_residue,
            **{k: v for k, v in row.items() if k != "Alignment_position"}
        })

print("Output:", outfile)
print("Mapped IsPETase residues:", isp_pos)
