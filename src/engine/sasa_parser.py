import os
from engine.md_column_aliases import COLUMN_ALIASES, resolve_column, detect_unit, read_tabular_data

class SasaParser:
    def parse(self, file_path: str, warnings: list) -> list:
        rows = read_tabular_data(file_path)
        if not rows:
            raise ValueError(f"No rows found in SASA file: {file_path}")
        headers = list(rows[0].keys())
        time_col = resolve_column(headers, COLUMN_ALIASES["time"])
        sasa_col = resolve_column(headers, COLUMN_ALIASES["sasa"])
        if not time_col or not sasa_col:
            raise ValueError(f"Required time/SASA columns not resolved in: {os.path.basename(file_path)}")
        
        unit = detect_unit(sasa_col)
        if not unit:
            unit = ""
            warnings.append(f"Could not determine unit for SASA from column: {sasa_col}. Preserving raw values.")

        sasa_data = []
        for idx, r in enumerate(rows):
            try:
                t = float(r[time_col])
                val = float(r[sasa_col])
                sasa_data.append({
                    "time": t,
                    "value": val,
                    "unit": unit
                })
            except (ValueError, TypeError):
                warnings.append(f"Malformed numerical data in {os.path.basename(file_path)} at row index {idx}")
        return sasa_data
