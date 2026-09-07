import os
from engine.md_column_aliases import COLUMN_ALIASES, resolve_column, detect_unit, read_tabular_data

class RmsfParser:
    def parse(self, file_path: str, warnings: list, sim_trace: dict) -> list:
        rows = read_tabular_data(file_path)
        if not rows:
            raise ValueError(f"No rows found in RMSF file: {file_path}")
        headers = list(rows[0].keys())
        pos_col = resolve_column(headers, COLUMN_ALIASES["position"])
        rmsf_col = resolve_column(headers, COLUMN_ALIASES["rmsf"])
        res_col = resolve_column(headers, COLUMN_ALIASES["residue"])

        if not pos_col or not rmsf_col:
            raise ValueError(f"Required position/RMSF columns not resolved in: {os.path.basename(file_path)}")
        
        unit = detect_unit(rmsf_col)
        if not unit:
            unit = ""
            warnings.append(f"Could not determine unit for RMSF from column: {rmsf_col}. Preserving raw values.")

        records = []
        for idx, r in enumerate(rows):
            try:
                pos = int(r[pos_col])
                val = float(r[rmsf_col])
                res_name = r[res_col] if res_col else ""
                record = {
                    "position": pos,
                    "residue": res_name,
                    "value": val,
                    "unit": unit,
                    "metric_type": "rmsf",
                    "source_file": os.path.basename(file_path),
                    "source_row": idx
                }
                record.update(sim_trace)
                records.append(record)
            except (ValueError, TypeError):
                warnings.append(f"Malformed numerical data in {os.path.basename(file_path)} at row index {idx}")
        return records
