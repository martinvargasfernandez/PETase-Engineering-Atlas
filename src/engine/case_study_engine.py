from pathlib import Path
import pandas as pd


class CaseStudyEngine:
    """
    Generic loader for protein-specific evidence.

    Any folder inside case_studies/ is treated as one case study.

    Example:
        case_studies/
            BhrPETase/
            TurboPETase/
            BhrPETase/
            NewPETase/

    Any TSV file inside a case-study folder is treated as an evidence table.
    """

    def __init__(self, base_dir="case_studies"):
        self.base_dir = Path(base_dir)

    def get_available_case_studies(self):
        if not self.base_dir.exists():
            return []

        return sorted([
            path.name
            for path in self.base_dir.iterdir()
            if path.is_dir()
        ])

    def get_case_study_path(self, case_name):
        return self.base_dir / case_name

    def get_available_evidence_files(self, case_name):
        case_path = self.get_case_study_path(case_name)

        if not case_path.exists():
            return []

        return sorted([
            path.name
            for path in case_path.iterdir()
            if path.is_file() and path.suffix == ".tsv"
        ])

    def load_evidence_table(self, case_name, filename):
        path = self.get_case_study_path(case_name) / filename

        if not path.exists():
            return pd.DataFrame()

        return pd.read_csv(path, sep="\t")

    def load_all_evidence(self, case_name):
        evidence = {}

        for filename in self.get_available_evidence_files(case_name):
            evidence_name = filename.replace(".tsv", "")
            evidence[evidence_name] = self.load_evidence_table(case_name, filename)

        return evidence

    def get_residue_context(self, case_name, position):
        position = int(position)
        context = {
            "case_study": case_name,
            "position": position,
            "evidence": {},
        }

        all_evidence = self.load_all_evidence(case_name)

        for evidence_name, df in all_evidence.items():
            if df.empty or "position" not in df.columns:
                continue

            match = df[df["position"] == position]

            if not match.empty:
                context["evidence"][evidence_name] = match.iloc[0].to_dict()

        return context
