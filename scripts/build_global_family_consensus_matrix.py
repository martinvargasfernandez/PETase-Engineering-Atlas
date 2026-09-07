from Bio import AlignIO
from collections import Counter, defaultdict
from pathlib import Path
import csv

alignment = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean_mafft.fasta")
assignments = Path("atlas_v3/families/petase_atlas_v3_family_assignments.tsv")
out_file = Path("atlas_v3/families/global_family_consensus_matrix.tsv")

AA = set("ACDEFGHIKLMNPQRSTVWY")

# Leer familias
tree_to_family = {}

with assignments.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        tree_to_family[row["tree_id"]] = row["family_name"]

aln = AlignIO.read(alignment, "fasta")

# Encontrar IsPETase para mapear posiciones
ispetase = None
for rec in aln:
    if "A0A0K8P6T7" in rec.id:
        ispetase = rec
        break

if ispetase is None:
    raise SystemExit("IsPETase not found")

families = sorted(set(tree_to_family.values()))

# Agrupar índices por familia
family_indices = defaultdict(list)

for idx, rec in enumerate(aln):
    fam = tree_to_family.get(rec.id)
    if fam:
        family_indices[fam].append(idx)

# Escribir matriz
with out_file.open("w", newline="") as out:
    writer = csv.writer(out, delimiter="\t")

    header = [
        "Alignment_position",
        "IsPETase_position",
        "IsPETase_residue",
        "Global_consensus",
        "Global_conservation"
    ]

    for fam in families:
        header += [
            f"{fam}_consensus",
            f"{fam}_conservation",
            f"{fam}_nseq"
        ]

    writer.writerow(header)

    isp_pos = 0

    for aln_pos, isp_aa in enumerate(str(ispetase.seq), start=1):

        if isp_aa != "-":
            isp_pos += 1
            isp_position = isp_pos
        else:
            isp_position = "NA"

        column = aln[:, aln_pos - 1]
        residues = [x for x in column if x in AA]

        if not residues:
            continue

        counts = Counter(residues)
        global_cons, global_n = counts.most_common(1)[0]
        global_cons_pct = round(100 * global_n / len(residues), 2)

        row = [
            aln_pos,
            isp_position,
            isp_aa,
            global_cons,
            global_cons_pct
        ]

        for fam in families:
            idxs = family_indices[fam]
            fam_residues = [
                str(aln[i].seq)[aln_pos - 1]
                for i in idxs
                if str(aln[i].seq)[aln_pos - 1] in AA
            ]

            if not fam_residues:
                row += ["NA", "NA", 0]
            else:
                fam_counts = Counter(fam_residues)
                fam_cons, fam_n = fam_counts.most_common(1)[0]
                fam_pct = round(100 * fam_n / len(fam_residues), 2)
                row += [fam_cons, fam_pct, len(fam_residues)]

        writer.writerow(row)

print("Output:", out_file)
print("Families:", ", ".join(families))
