import os
from engine.md_column_aliases import COLUMN_ALIASES, resolve_column, detect_unit, read_tabular_data

class ResidueEnergyParser:
    def parse(self, file_path: str, warnings: list, sim_trace: dict) -> list:
        rows = read_tabular_data(file_path)
        if not rows:
            raise ValueError(f"No rows found in residue energy file: {file_path}")
        headers = list(rows[0].keys())
        pos_col = resolve_column(headers, COLUMN_ALIASES["position"])
        coul_col = resolve_column(headers, COLUMN_ALIASES["coul_sr"])
        lj_col = resolve_column(headers, COLUMN_ALIASES["lj_sr"])
        total_col = resolve_column(headers, COLUMN_ALIASES["total"])

        res_col = resolve_column(headers, COLUMN_ALIASES["residue"])

        if not total_col:
            raise ValueError(f"Required total energy column not resolved in: {os.path.basename(file_path)}")
        if not pos_col and not res_col:
            raise ValueError(f"Required position or residue columns not resolved in: {os.path.basename(file_path)}")
        
        unit = detect_unit(total_col)
        if not unit:
            unit = ""
            warnings.append(f"Could not determine unit for residue energy from column: {total_col}. Preserving raw values.")

        records = []
        import re
        for idx, r in enumerate(rows):
            try:
                if pos_col:
                    pos = int(r[pos_col])
                else:
                    joint_val = r[res_col]
                    m = re.match(r'^([A-Za-z]*)(\d+)$', joint_val.strip())
                    if m:
                        pos = int(m.group(2))
                    else:
                        raise ValueError("Invalid residue energy format")

                coul_val = float(r[coul_col]) if coul_col else 0.0
                lj_val = float(r[lj_col]) if lj_col else 0.0
                total_val = float(r[total_col])
                record = {
                    "position": pos,
                    "energy_coulomb": coul_val,
                    "energy_lj": lj_val,
                    "energy_total": total_val,
                    "value": total_val, # generic compatibility mapping
                    "unit": unit,
                    "metric_type": "interaction_energy",
                    "source_file": os.path.basename(file_path),
                    "source_row": idx
                }
                record.update(sim_trace)
                records.append(record)
            except (ValueError, TypeError):
                warnings.append(f"Malformed numerical data in {os.path.basename(file_path)} at row index {idx}")
        return records
