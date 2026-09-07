COLUMN_ALIASES = {
    "time": ["time_ps", "Time_ps", "time"],
    "rmsd": ["rmsd_nm", "RMSD_nm", "rmsd"],
    "rmsf": ["rmsf_nm", "RMSF_nm", "rmsf"],
    "rg": ["rg_nm", "Rg_nm", "rg", "radius_of_gyration"],
    "sasa": ["sasa_nm2", "SASA_nm2", "sasa"],
    "residue": ["residue", "resname", "residue_name"],
    "position": ["position", "resid", "residue_number"],
    "frequency": ["frequency", "occupancy", "persistence_percent", "frequency_percent", "frequency_pct", "percent", "percentage"],
    "donor": ["donor"],
    "acceptor": ["acceptor"],
    "coul_sr": ["coul_sr", "Coul-SR", "coulomb_energy"],
    "lj_sr": ["lj_sr", "LJ-SR", "lennard_jones_energy"],
    "total": ["total", "total_energy"]
}

def resolve_column(headers: list, aliases: list) -> str:
    import re
    for h in headers:
        clean = re.sub(r'\s*\([^)]+\)', '', h).strip()
        clean = re.sub(r'_(ps|nm|nm2|kcal_mol|kj_mol|kJ_mol|%)$', '', clean, flags=re.IGNORECASE).strip()
        if clean.lower() in [a.lower().strip() for a in aliases]:
            return h
    return None

def detect_unit(header: str) -> str:
    import re
    # Match unit in parenthesis, e.g. "time (ps)"
    m_paren = re.search(r'\(([^)]+)\)', header)
    if m_paren:
        return m_paren.group(1).strip()
    # Match unit after underscore, e.g. "time_ps"
    m_under = re.search(r'_(ps|nm|nm2|kcal_mol|kj_mol|kJ_mol|%)$', header, re.IGNORECASE)
    if m_under:
        return m_under.group(1).strip()
    return None

def read_tabular_data(file_path: str) -> list:
    import csv
    import os

    if file_path.lower().endswith(".xvg"):
        filename = os.path.basename(file_path).lower()
        x_label = "time"
        y_label = "value"
        if "rmsd" in filename:
            x_label, y_label = "time", "rmsd"
        elif "rmsf" in filename:
            x_label, y_label = "position", "rmsf"
        elif "gyrate" in filename or "rg" in filename:
            x_label, y_label = "time", "rg"
        elif "sasa" in filename:
            x_label, y_label = "time", "sasa"

        rows = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("#", "@")):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    rows.append({x_label: parts[0], y_label: parts[1]})
        return rows

    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = "\t" if "\t" in sample else ","
        reader = csv.DictReader(f, delimiter=delimiter)
        for r in reader:
            rows.append({k.strip(): v.strip() for k, v in r.items() if k is not None})
    return rows
