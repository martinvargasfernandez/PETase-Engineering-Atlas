import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from Bio.PDB import PDBParser
from Bio.PDB.SASA import ShrakeRupley

def precompute_features():
    print("Precomputing structural features from PDB 6EQE...")
    
    pdb_path = Path("databases/pdb/6eqe.pdb")
    master_path = Path("atlas_v3/atlas_v3_master_position_table.tsv")
    
    if not pdb_path.exists():
        raise FileNotFoundError(f"PDB 6EQE not found at: {pdb_path}")
    if not master_path.exists():
        raise FileNotFoundError(f"Master table not found at: {master_path}")
        
    master_df = pd.read_csv(master_path, sep="\t")
    
    # 1. Parse PDB Structure
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("6eqe", pdb_path)
    
    # 2. Parse HELIX and SHEET records from PDB header
    helices = []
    sheets = []
    with open(pdb_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("HELIX"):
                try:
                    start = int(line[21:25].strip())
                    end = int(line[33:37].strip())
                    helices.append((start, end))
                except Exception:
                    pass
            elif line.startswith("SHEET"):
                try:
                    start = int(line[22:26].strip())
                    end = int(line[33:37].strip())
                    sheets.append((start, end))
                except Exception:
                    pass
                    
    # 3. Compute SASA using Shrake-Rupley
    sr = ShrakeRupley()
    sr.compute(structure, level="R")
    
    MAX_SASA = {
        'ALA': 129.0, 'ARG': 274.0, 'ASN': 195.0, 'ASP': 193.0, 'CYS': 167.0,
        'GLN': 225.0, 'GLU': 223.0, 'GLY': 104.0, 'HIS': 224.0, 'ILE': 197.0,
        'LEU': 201.0, 'LYS': 236.0, 'MET': 224.0, 'PHE': 240.0, 'PRO': 159.0,
        'SER': 155.0, 'THR': 172.0, 'TRP': 285.0, 'TYR': 263.0, 'VAL': 174.0
    }
    
    model = structure[0]
    chain = model["A"]
    
    # Map resolved C-alpha atoms
    ca_atoms = {}
    for residue in chain:
        if residue.id[0] == " " and "CA" in residue:
            ca_atoms[residue.id[1]] = residue
            
    # Catalytic residues mapping (S160, D206, H237)
    c_s160 = ca_atoms[160]["CA"].coord
    c_d206 = ca_atoms[206]["CA"].coord
    c_h237 = ca_atoms[237]["CA"].coord
    c_centroid = (c_s160 + c_d206 + c_h237) / 3.0
    
    # Determine surface residues for depth calculation (relative SASA > 0.15)
    surface_coords = []
    for pos, res in ca_atoms.items():
        resname = res.resname
        max_val = MAX_SASA.get(resname, 1.0)
        rel_sasa = res.sasa / max_val
        if rel_sasa > 0.15:
            surface_coords.append(res["CA"].coord)
            
    rows = []
    # Loop over all 290 reference positions
    for idx, r in master_df.iterrows():
        pos = int(r["IsPETase_position"])
        wt_res = r["IsPETase_residue"]
        
        # Check secondary structure
        sec_str = "C"
        for start, end in helices:
            if start <= pos <= end:
                sec_str = "H"
                break
        if sec_str == "C":
            for start, end in sheets:
                if start <= pos <= end:
                    sec_str = "E"
                    break
                    
        # Check if resolved
        if pos in ca_atoms:
            res = ca_atoms[pos]
            coord = res["CA"].coord
            resname = res.resname
            sasa = res.sasa
            max_val = MAX_SASA.get(resname, 1.0)
            rel_sasa = sasa / max_val
            
            # Calculate distance to catalytic triad
            d_s160 = float(np.linalg.norm(coord - c_s160))
            d_d206 = float(np.linalg.norm(coord - c_d206))
            d_h237 = float(np.linalg.norm(coord - c_h237))
            min_d = min(d_s160, d_d206, d_h237)
            d_centroid = float(np.linalg.norm(coord - c_centroid))
            
            # Depth: min distance to any surface residue C-alpha
            if rel_sasa > 0.15:
                depth = 0.0
            else:
                depth = float(min(np.linalg.norm(coord - sc) for sc in surface_coords)) if surface_coords else 0.0
                
            # Contacts: count C-alpha within 8.0 Å
            contacts = sum(1 for p in ca_atoms if p != pos and np.linalg.norm(ca_atoms[p]["CA"].coord - coord) <= 8.0)
            
            rows.append({
                "reference_position": pos,
                "reference_residue": wt_res,
                "secondary_structure": sec_str,
                "relative_SASA": round(rel_sasa, 6),
                "residue_depth": round(depth, 6),
                "distance_to_S160": round(d_s160, 6),
                "distance_to_D206": round(d_d206, 6),
                "distance_to_H237": round(d_h237, 6),
                "minimum_distance_to_catalytic_triad": round(min_d, 6),
                "distance_to_active_site_centroid": round(d_centroid, 6),
                "local_contact_count": int(contacts),
                "structural_feature_available": "YES"
            })
        else:
            # Missing / signal peptide
            rows.append({
                "reference_position": pos,
                "reference_residue": wt_res,
                "secondary_structure": sec_str,
                "relative_SASA": np.nan,
                "residue_depth": np.nan,
                "distance_to_S160": np.nan,
                "distance_to_D206": np.nan,
                "distance_to_H237": np.nan,
                "minimum_distance_to_catalytic_triad": np.nan,
                "distance_to_active_site_centroid": np.nan,
                "local_contact_count": np.nan,
                "structural_feature_available": "NO"
            })
            
    out_df = pd.DataFrame(rows)
    out_dir = Path("results/validation/hotspot_v2")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_dir / "6eqe_structural_features.tsv", sep="\t", index=False)
    print(f"Precomputed structural features saved to {out_dir / '6eqe_structural_features.tsv'}")

if __name__ == "__main__":
    precompute_features()
