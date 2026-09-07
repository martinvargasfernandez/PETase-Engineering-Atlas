import os
from engine.md_column_aliases import COLUMN_ALIASES, resolve_column, detect_unit, read_tabular_data

class RmsdParser:
    def parse(self, file_path: str, warnings: list) -> list:
        rows = read_tabular_data(file_path)
        if not rows:
            raise ValueError(f"No rows found in RMSD file: {file_path}")
        headers = list(rows[0].keys())
        time_col = resolve_column(headers, COLUMN_ALIASES["time"])
        rmsd_col = resolve_column(headers, COLUMN_ALIASES["rmsd"])
        if not time_col or not rmsd_col:
            raise ValueError(f"Required time/rmsd columns not resolved in: {os.path.basename(file_path)}")
        
        unit = detect_unit(rmsd_col)
        if not unit:
            unit = ""
            warnings.append(f"Could not determine unit for RMSD from column: {rmsd_col}. Preserving raw values.")

        rmsd_data = []
        for idx, r in enumerate(rows):
            try:
                t = float(r[time_col])
                val = float(r[rmsd_col])
                rmsd_data.append({
                    "time": t,
                    "value": val,
                    "unit": unit
                })
            except (ValueError, TypeError):
                warnings.append(f"Malformed numerical data in {os.path.basename(file_path)} at row index {idx}")
        return rmsd_data
