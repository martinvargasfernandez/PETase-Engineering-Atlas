import os
from engine.md_column_aliases import COLUMN_ALIASES, resolve_column, detect_unit, read_tabular_data

class HbondsParser:
    def parse(self, file_path: str, warnings: list, sim_trace: dict) -> list:
        rows = read_tabular_data(file_path)
        if not rows:
            raise ValueError(f"No rows found in hbonds file: {file_path}")
        headers = list(rows[0].keys())
        pos_col = resolve_column(headers, COLUMN_ALIASES["position"])
        freq_col = resolve_column(headers, COLUMN_ALIASES["frequency"])
        donor_col = resolve_column(headers, COLUMN_ALIASES["donor"])
        acceptor_col = resolve_column(headers, COLUMN_ALIASES["acceptor"])

        interaction_col = resolve_column(headers, ["interaction"])

        if not freq_col:
            raise ValueError(f"Required occupancy/frequency column not resolved in: {os.path.basename(file_path)}")
        if not pos_col and not interaction_col:
            raise ValueError(f"Required position or interaction columns not resolved in: {os.path.basename(file_path)}")
        
        unit = detect_unit(freq_col)
        if not unit:
            unit = ""
            warnings.append(f"Could not determine unit for hbonds from column: {freq_col}. Preserving raw values.")

        records = []
        import re
        for idx, r in enumerate(rows):
            try:
                if pos_col:
                    pos = int(r[pos_col])
                    donor_str = r[donor_col] if donor_col else ""
                    acceptor_str = r[acceptor_col] if acceptor_col else ""
                else:
                    inter_val = r[interaction_col]
                    parts = inter_val.split("--")
                    donor_str = parts[0]
                    acceptor_str = parts[1] if len(parts) > 1 else ""
                    m = re.match(r'^([A-Za-z]+)(\d+)', donor_str.strip())
                    if m:
                        pos = int(m.group(2))
                    else:
                        raise ValueError("Invalid interaction format")

                val = float(r[freq_col])
                record = {
                    "position": pos,
                    "donor": donor_str,
                    "acceptor": acceptor_str,
                    "value": val,
                    "unit": unit,
                    "metric_type": "hbond_persistence",
                    "source_file": os.path.basename(file_path),
                    "source_row": idx
                }
                record.update(sim_trace)
                records.append(record)
            except (ValueError, TypeError):
                warnings.append(f"Malformed numerical data in {os.path.basename(file_path)} at row index {idx}")
        return records
