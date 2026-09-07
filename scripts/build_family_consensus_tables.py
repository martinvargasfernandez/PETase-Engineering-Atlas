import csv
import subprocess
from pathlib import Path
from collections import Counter
from Bio import SeqIO, AlignIO

assignments = Path("atlas_v3/families/petase_atlas_v3_family_assignments.tsv")
fasta_all = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean.fasta")
out_dir = Path("atlas_v3/families/consensus")
out_dir.mkdir(parents=True, exist_ok=True)

AA = set("ACDEFGHIKLMNPQRSTVWY")

families = {}
tree_to_family = {}

with assignments.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        fam = row["family_name"]
        tree_id = row["tree_id"]
        tree_to_family[tree_id] = fam
        families.setdefault(fam, []).append(tree_id)

records_by_id = {rec.id: rec for rec in SeqIO.parse(fasta_all, "fasta")}

for fam, ids in sorted(families.items()):
    safe = fam.replace("-", "_").replace(" ", "_")
    fam_fasta = out_dir / f"{safe}.fasta"
    fam_aln = out_dir / f"{safe}_mafft.fasta"
    fam_cons = out_dir / f"{safe}_consensus.tsv"

    records = [records_by_id[i] for i in ids if i in records_by_id]

    if len(records) < 3:
        print(f"SKIP {fam}: only {len(records)} sequences")
        continue

    SeqIO.write(records, fam_fasta, "fasta")

    print(f"Aligning {fam}: {len(records)} sequences")
    with fam_aln.open("w") as out:
        subprocess.run(["mafft", "--auto", str(fam_fasta)], stdout=out, check=True)

    aln = AlignIO.read(fam_aln, "fasta")

    with fam_cons.open("w", newline="") as out:
        writer = csv.writer(out, delimiter="\t")
        writer.writerow([
            "Family",
            "Family_alignment_position",
            "Consensus",
            "Conservation_percent",
            "Unique_aminoacids",
            "Counts"
        ])

        for pos in range(aln.get_alignment_length()):
            column = aln[:, pos]
            residues = [x for x in column if x in AA]

            if not residues:
                continue

            counts = Counter(residues)
            consensus, n = counts.most_common(1)[0]
            conservation = round(100 * n / len(residues), 2)
            counts_string = ",".join(f"{aa}:{counts[aa]}" for aa in sorted(counts))

            writer.writerow([
                fam,
                pos + 1,
                consensus,
                conservation,
                len(counts),
                counts_string
            ])

    print(f"  Consensus: {fam_cons}")

print("DONE")
