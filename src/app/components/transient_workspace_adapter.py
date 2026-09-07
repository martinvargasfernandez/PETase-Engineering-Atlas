from engine.sequence_analysis_engine import SequenceAnalysisEngine
from engine.transient_sequence_session import TransientSequenceSession

def resolve_transient_input(input_source: str, pasted_text: str, uploaded_file) -> tuple:
    """
    Exclusively resolves sequence input based on selected source.
    Returns (effective_pasted_text, effective_uploaded_bytes, effective_uploaded_name).
    """
    if input_source == "Paste FASTA":
        return pasted_text, None, None
    else:
        if uploaded_file is not None:
            return "", uploaded_file.getvalue(), uploaded_file.name
        return "", None, None


class TransientSequenceWorkspaceAdapter:
    """
    Application-layer adapter to parse, validate, and orchestrate
    SequenceAnalysisEngine for the transient FASTA sequence workspace.
    """
    def __init__(self, engine: SequenceAnalysisEngine = None):
        self.engine = engine or SequenceAnalysisEngine()

    def parse_and_analyze(
        self,
        pasted_text: str = "",
        uploaded_file_bytes: bytes = None,
        uploaded_file_name: str = None,
        minimum_fvi: int = 1,
        excluded_positions: list = None
    ) -> tuple[TransientSequenceSession | None, str | None]:
        """
        Processes transient sequence user inputs according to deterministic rules:
        1. If a file is uploaded, use file bytes contents.
        2. Otherwise use pasted text.
        3. If neither contains a sequence, return None.
        Returns:
            (TransientSequenceSession, None) on success
            (None, error_message_string) on validation or analysis failure
        """
        raw_input = ""
        header = None

        # Precedence Rule: Uploaded file takes absolute precedence over pasted text
        if uploaded_file_bytes is not None:
            try:
                raw_input = uploaded_file_bytes.decode("utf-8").strip()
            except Exception as e:
                return None, f"Failed to decode uploaded file: {str(e)}"
        else:
            raw_input = pasted_text.strip() if pasted_text else ""

        if not raw_input:
            return None, "Empty sequence input. Provide a query sequence."

        # Parse lines
        lines = [line.strip() for line in raw_input.splitlines() if line.strip()]
        if not lines:
            return None, "Empty sequence input."

        # Parse FASTA header
        if lines[0].startswith(">"):
            header = lines[0].lstrip(">").strip()
            raw_seq = "".join(lines[1:])
        else:
            raw_seq = "".join(lines)
            header = uploaded_file_name or "CustomSequence"

        # Normalize sequence content (remove spaces, line breaks)
        raw_seq = raw_seq.replace(" ", "").replace("\r", "").replace("\n", "")
        if not raw_seq:
            return None, "Sequence content is empty after FASTA header."

        try:
            session = self.engine.analyze_sequence(
                raw_sequence=raw_seq,
                fasta_header=header,
                minimum_fvi=minimum_fvi,
                excluded_positions=excluded_positions
            )
            return session, None
        except Exception as e:
            return None, str(e)


def filter_recommendations(recommendations: list[dict], priorities: list[str], search_query: str) -> list[dict]:
    """
    Safely filters recommendation records based on priority and a search query,
    ensuring resistance against NoneType values in search fields.
    """
    filtered_recs = []
    query = str(search_query or "").strip()
    for r in recommendations:
        if r.get("proposal_priority") not in priorities:
            continue
        if query:
            if query.isdigit():
                q_val = int(query)
                def pos_matches(val) -> bool:
                    if val is None or isinstance(val, bool):
                        return False
                    try:
                        return float(val) == float(q_val)
                    except (ValueError, TypeError):
                        return False
                atlas_pos = r.get("atlas_position")
                study_pos = r.get("study_position")
                if not pos_matches(atlas_pos) and not pos_matches(study_pos):
                    continue
            else:
                q = query.lower()
                label = str(r.get("mutation_label") or "").lower()
                atlas_lbl = str(r.get("atlas_mutation_label") or "").lower()
                proj_lbl = str(r.get("project_mutation_label") or "").lower()
                pos = str(r.get("atlas_position") if r.get("atlas_position") is not None else "")
                study_pos = str(r.get("study_position") if r.get("study_position") is not None else "")
                if q not in label and q not in atlas_lbl and q not in proj_lbl and q not in pos and q not in study_pos:
                    continue
        filtered_recs.append(r)
    return filtered_recs


