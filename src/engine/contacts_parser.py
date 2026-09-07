import os
from engine.md_column_aliases import COLUMN_ALIASES, resolve_column, detect_unit, read_tabular_data

class ContactsParser:
    def parse(self, file_path: str, warnings: list, sim_trace: dict) -> list:
        rows = read_tabular_data(file_path)
        if not rows:
            raise ValueError(f"No rows found in contacts file: {file_path}")
        headers = list(rows[0].keys())
        pos_col = resolve_column(headers, COLUMN_ALIASES["position"])
        freq_col = resolve_column(headers, COLUMN_ALIASES["frequency"])
        res_col = resolve_column(headers, COLUMN_ALIASES["residue"])

        if not freq_col:
            raise ValueError(f"Required frequency column not resolved in: {os.path.basename(file_path)}")
        if not pos_col and not res_col:
            raise ValueError(f"Required position or residue columns not resolved in: {os.path.basename(file_path)}")
        
        unit = detect_unit(freq_col)
        if not unit:
            unit = ""
            warnings.append(f"Could not determine unit for contacts from column: {freq_col}. Preserving raw values.")

        records = []
        import re
        for idx, r in enumerate(rows):
            try:
                if pos_col:
                    pos = int(r[pos_col])
                    res_name = r[res_col] if res_col else ""
                else:
                    joint_val = r[res_col]
                    m = re.match(r'^([A-Za-z]+)(\d+)$', joint_val.strip())
                    if m:
                        res_name = m.group(1)
                        pos = int(m.group(2))
                    else:
                        raise ValueError("Invalid joint residue format")

                val = float(r[freq_col])
                record = {
                    "position": pos,
                    "residue": res_name,
                    "value": val,
                    "unit": unit,
                    "metric_type": "contact_frequency",
                    "source_file": os.path.basename(file_path),
                    "source_row": idx
                }
                record.update(sim_trace)
                records.append(record)
            except (ValueError, TypeError):
                warnings.append(f"Malformed numerical data in {os.path.basename(file_path)} at row index {idx}")
        return records
