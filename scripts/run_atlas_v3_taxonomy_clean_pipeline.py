from pathlib import Path
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
import subprocess

input_fasta = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean.fasta")
raw_alignment = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean_mafft.fasta")
trimmed_alignment = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean_mafft_trim50.fasta")
tree_file = Path("atlas_v3/petase_atlas_v3_bacteria_taxonomy_clean_fasttree.nwk")

print("Running MAFFT...")
with raw_alignment.open("w") as out:
    subprocess.run(["mafft", "--auto", str(input_fasta)], stdout=out, check=True)

print("Trimming >50% gap columns...")
aln = AlignIO.read(raw_alignment, "fasta")
nseq = len(aln)

keep_cols = [
    i for i in range(aln.get_alignment_length())
    if aln[:, i].count("-") / nseq <= 0.5
]

records = []
for rec in aln:
    newseq = "".join(rec.seq[i] for i in keep_cols)
    records.append(SeqRecord(Seq(newseq), id=rec.id, description=rec.description))

trimmed = MultipleSeqAlignment(records)
AlignIO.write(trimmed, trimmed_alignment, "fasta")

print("Running FastTree...")
with tree_file.open("w") as out:
    subprocess.run(["FastTree", str(trimmed_alignment)], stdout=out, check=True)

print("DONE")
print("Sequences:", nseq)
print("Raw alignment length:", aln.get_alignment_length())
print("Trimmed alignment length:", trimmed.get_alignment_length())
print("Tree:", tree_file)
