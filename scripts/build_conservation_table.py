from Bio import AlignIO
from collections import Counter
import csv
from pathlib import Path

alignment = "alignments/pet_family_bacterial_mafft_trim50.fasta"
outfile = Path("conservation/pet_family_conservation.tsv")

aln = AlignIO.read(alignment, "fasta")

AA = set("ACDEFGHIKLMNPQRSTVWY")

with outfile.open("w", newline="") as out:

    writer = csv.writer(out, delimiter="\t")

    writer.writerow([
        "Alignment_position",
        "Consensus",
        "Conservation_percent",
        "Unique_aminoacids",
        "Counts"
    ])

    for pos in range(aln.get_alignment_length()):

        column = aln[:, pos]

        residues = [x for x in column if x in AA]

        if len(residues) == 0:
            continue

        counts = Counter(residues)

        consensus, n = counts.most_common(1)[0]

        conservation = 100 * n / len(residues)

        counts_string = ",".join(
            f"{aa}:{counts[aa]}"
            for aa in sorted(counts)
        )

        writer.writerow([
            pos + 1,
            consensus,
            round(conservation,2),
            len(counts),
            counts_string
        ])

print("Finished")
print("Alignment length:", aln.get_alignment_length())
print("Output:", outfile)
