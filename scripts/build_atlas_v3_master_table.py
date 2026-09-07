import csv
from pathlib import Path
from Bio import SeqIO

metadata_file = Path("metadata/evolution/uniprot_multisearch_v2_filtered.tsv")
fasta_file = Path("sequences/evolution_natural/v2_hmm_validated.fasta")
out_file = Path("atlas_v3/petase_atlas_v3_master.tsv")

metadata = {}

with metadata_file.open() as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        metadata[row["accession"]] = row

def get_acc(record_id):
    if "|" in record_id:
        return record_id.split("|")[1]
    return record_id

def genus(org):
    return org.split()[0] if org else "Unknown"

def enzyme_class(protein_name):
    p = protein_name.lower()
    if "poly(ethylene terephthalate)" in p or "pet hydrolase" in p or "petase" in p:
        return "PET_hydrolase"
    if "cutinase" in p:
        return "Cutinase"
    if "esterase" in p:
        return "Esterase_like"
    return "Other"

def reference_label(acc):
    refs = {
        "A0A0K8P6T7": "IsPETase",
        "G9BY57": "LCC",
        "Q6A0I4": "TfCut2",
        "G8GER6": "Thermobifida_PETH1",
        "Q47RJ7": "Thermobifida_PETH1",
        "Q47RJ6": "Thermobifida_PETH2",
        "F7IX06": "Thermobifida_PETH2",
        "D4Q9N1": "Thermobifida_PETH1",
    }
    return refs.get(acc, "NA")

records = []

for rec in SeqIO.parse(fasta_file, "fasta"):
    acc = get_acc(rec.id)

    if acc not in metadata:
        continue

    row = metadata[acc]
    org = row["organism_name"]
    protein = row["protein_name"]

    records.append({
        "accession": acc,
        "tree_id": rec.id,
        "uniprot_id": row["id"],
        "protein_name": protein,
        "organism": org,
        "genus": genus(org),
        "length": len(rec.seq),
        "reviewed": row["reviewed"],
        "source_queries": row["source_queries"],
        "enzyme_class": enzyme_class(protein),
        "reference_label": reference_label(acc),
    })

with out_file.open("w", newline="") as out:
    fieldnames = [
        "accession",
        "tree_id",
        "uniprot_id",
        "protein_name",
        "organism",
        "genus",
        "length",
        "reviewed",
        "source_queries",
        "enzyme_class",
        "reference_label",
    ]

    writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter="\t")
    writer.writeheader()
    writer.writerows(records)

print("Atlas v3 master table:", out_file)
print("Entries:", len(records))
