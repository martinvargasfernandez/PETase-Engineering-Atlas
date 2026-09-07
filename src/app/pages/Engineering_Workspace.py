import os
import sys
from pathlib import Path
import json
import pandas as pd

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from engine.project_repository import ProjectRepository
from engine.case_study_repository import CaseStudyRepository
from engine.project_engineering_engine import ProjectEngineeringEngine
from engine.functional_hotspots import FunctionFirstEngine
from app.components.transient_workspace_adapter import resolve_transient_input
from app.components.function_first_hotspots_view import render_function_first_hotspots_view
from app.components.structure_viewer_panel import render_structure_viewer_panel
from app.utils.theme import apply_custom_css

def get_unit_label(rec: dict) -> str:
    metric_type = rec.get("metric_type") or rec.get("evidence_type") or ""
    metric_type = str(metric_type).lower()

    if "rmsf" in metric_type:
        return "Å"
    elif "hbond" in metric_type:
        return "occupancy %"
    elif "energy" in metric_type or "coulomb" in metric_type or "lennard" in metric_type:
        return "kJ/mol"
    elif "contact" in metric_type:
        return "fraction"
    return ""

def filter_recommendations(recs: list, priorities: list, query: str) -> list:
    filtered = []
    query_clean = query.strip().lower()
    
    for r in recs:
        if r.get("proposal_priority") not in priorities:
            continue
            
        if query_clean:
            mut_lbl = str(r.get("mutation_label", "")).lower()
            atlas_lbl = str(r.get("atlas_mutation_label", "")).lower()
            proj_lbl = str(r.get("project_mutation_label", "")).lower()
            study_pos = str(r.get("study_position", "")).lower()
            atlas_pos = str(r.get("atlas_position", "")).lower()
            
            if not (query_clean in mut_lbl or 
                    query_clean in atlas_lbl or 
                    query_clean in proj_lbl or 
                    query_clean in study_pos or 
                    query_clean in atlas_pos):
                continue
                
        filtered.append(r)
        
    return filtered

@st.cache_data(ttl=600)
def run_engineering_analysis_cached(
    _engine: ProjectEngineeringEngine,
    _project_repo: ProjectRepository,
    project_id: str,
    project_updated_at: str,
    minimum_fvi: int,
    excluded_atlas_positions: tuple,
    case_study_fingerprint: str
) -> dict:
    project = _project_repo.load_project(project_id)
    session = _engine.analyze_project(
        project,
        minimum_fvi=minimum_fvi,
        excluded_positions=list(excluded_atlas_positions)
    )
    return session.to_dict()

def render_legacy_v24_analysis(recommendations: list, workspace_mode: str = "Analyze Custom Sequence", project=None, cs_repo=None, eng_engine=None, transient_session=None, active_cs_list=None):
    """Renders legacy V2.4 recommendations inside a single collapsed expander for transparency/reproducibility."""
    st.write("---")
    with st.expander("Advanced: Legacy V2.4 Evolutionary Analysis (Optional / Comparison Only)"):
        st.caption("This section presents the previous V2.4 evolutionary prioritization scoring architecture retained for transparency and comparative audit.")
        if not recommendations:
            st.info("No legacy recommendations found matching current filters.")
            return

        high_count = sum(1 for r in recommendations if r.get("proposal_priority") == "High")
        med_count = sum(1 for r in recommendations if r.get("proposal_priority") == "Medium")
        low_count = sum(1 for r in recommendations if r.get("proposal_priority") == "Low")

        c_h, c_m, c_l = st.columns(3)
        c_h.metric("High Priority Candidates", high_count)
        c_m.metric("Medium Priority Candidates", med_count)
        c_l.metric("Low Priority Candidates", low_count)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            priorities = st.multiselect(
                "Filter by Priority Class",
                options=["High", "Medium", "Low"],
                default=["High", "Medium", "Low"],
                key="legacy_priorities_select"
            )
        with col_f2:
            search_query = st.text_input(
                "Search by Mutation or Position",
                value="",
                key="legacy_search_query"
            )

        filtered_recs = filter_recommendations(recommendations, priorities, search_query)
        if not filtered_recs:
            st.warning("No legacy recommendations match search filters.")
            return

        df_display = pd.DataFrame([
            {
                "Rank": recommendations.index(r) + 1,
                "Atlas Mutation": r.get("atlas_mutation_label", r["mutation_label"]),
                "Project Mutation": r.get("project_mutation_label") if r.get("mutation_actionability") == "actionable" else ("Already present — no mutation required" if r.get("mutation_actionability") == "already_present" else "N/A"),
                "Study Position": r["study_position"],
                "Atlas Position": r["atlas_position"],
                "Proposal Score": r["proposal_score"],
                "Priority": r["proposal_priority"],
                "Atlas Evidence Score": r["atlas_evidence_score"],
                "Actionability": r.get("mutation_actionability", "actionable")
            }
            for r in filtered_recs
        ])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        rec_by_label = {r["mutation_label"]: r for r in filtered_recs}
        def format_mut_selectbox(x):
            rec = rec_by_label[x]
            proj_lbl = rec.get("project_mutation_label")
            actionability = rec.get("mutation_actionability", "actionable")
            if actionability == "already_present":
                return f"{x} (Project: Already present — no mutation required)"
            elif proj_lbl:
                return f"{x} (Project-specific: {proj_lbl})"
            else:
                return f"{x} (Project: N/A)"

        selected_mut_label = st.selectbox(
            "Select Legacy Mutation to Inspect",
            options=[r["mutation_label"] for r in filtered_recs],
            format_func=format_mut_selectbox,
            index=0,
            key="legacy_mut_select"
        )
        selected_rec = rec_by_label[selected_mut_label]

        st.markdown(f"#### Legacy Inspection Profile: {selected_rec['mutation_label']}")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Atlas Mutation Label", selected_rec.get("atlas_mutation_label", selected_rec["mutation_label"]))
            st.metric("Atlas Position", selected_rec["atlas_position"])
        with col_m2:
            st.metric("Study Position", selected_rec["study_position"])
            st.metric("Proposal Priority", selected_rec["proposal_priority"])
        with col_m3:
            st.metric("Proposal Score", selected_rec["proposal_score"])
            st.metric("Atlas Evidence Score", selected_rec["atlas_evidence_score"])
        with col_m4:
            st.metric("Actionability", selected_rec.get("mutation_actionability", "actionable"))


# Page Setup
st.set_page_config(page_title="Engineering Workspace", page_icon="🧬", layout="wide")
apply_custom_css()

st.title("🧬 Engineering Workspace")
st.caption("Analyze a PETase sequence to identify prioritized engineering positions and evolution-supported substitutions.")

proj_repo = ProjectRepository()
cs_repo = CaseStudyRepository()
eng_engine = ProjectEngineeringEngine()
ff_engine = FunctionFirstEngine()

# Single Public Workflow: Direct FASTA Input
st.sidebar.markdown("### Input Sequence")
input_source = st.sidebar.radio("Sequence input source:", ["Paste FASTA", "Upload FASTA file"], key="transient_input_source")

pasted_text = ""
uploaded_file = None
if input_source == "Paste FASTA":
    pasted_text = st.sidebar.text_area("Paste FASTA or raw sequence text", key="transient_pasted_input")
else:
    uploaded_file = st.sidebar.file_uploader("Upload FASTA file (.fasta, .fa)", type=["fasta", "fa"], key="transient_file_input")

min_fvi = st.sidebar.slider("Minimum FVI Threshold", min_value=1, max_value=10, value=3)
analyze_triggered = st.sidebar.button("Analyze Sequence")

if analyze_triggered:
    effective_pasted_text, file_bytes, file_name = resolve_transient_input(input_source, pasted_text, uploaded_file)
    if input_source == "Upload FASTA file" and uploaded_file is None:
        st.session_state["transient_error"] = "No file uploaded. Please upload a FASTA file."
    else:
        from app.components.transient_workspace_adapter import TransientSequenceWorkspaceAdapter
        adapter = TransientSequenceWorkspaceAdapter()
        session, err = adapter.parse_and_analyze(
            pasted_text=effective_pasted_text,
            uploaded_file_bytes=file_bytes,
            uploaded_file_name=file_name,
            minimum_fvi=min_fvi,
            excluded_positions=[]
        )
        if err:
            st.session_state["transient_error"] = err
        else:
            st.session_state["transient_error"] = None
            st.session_state["transient_session"] = session
            st.session_state["transient_session_source"] = input_source
            st.session_state["transient_session_filename"] = file_name
            st.rerun()

if st.session_state.get("transient_error"):
    st.sidebar.error(st.session_state["transient_error"])

transient_session = st.session_state.get("transient_session")
if not transient_session:
    st.info("Provide sequence inputs in the sidebar and click **Analyze Sequence** to begin.")
    st.stop()
else:
    recommendations = transient_session.recommendations
    primary_seq_name = transient_session.study_sequence.name
    primary_seq_len = len(transient_session.study_sequence.raw_sequence)
    predicted_family = transient_session.family_classification.predicted_family
    coordinate_system = transient_session.atlas_coordinate_system
    active_source = st.session_state.get("transient_session_source", "Paste FASTA")
    filename = st.session_state.get("transient_session_filename")

    st.subheader("Query Sequence Profile")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"**Query Sequence:** `{primary_seq_name}` ({primary_seq_len} residues)")
        if active_source == "Paste FASTA":
            st.markdown("**Active Input:** Pasted FASTA")
        else:
            fn_display = filename if filename else "unnamed file"
            st.markdown(f"**Active Input:** Uploaded File — `{fn_display}`")

    with col_p2:
        family_help = (
            "Atlas family-clade prediction is an independent sequence-based classification "
            "and does not replace the known identity of the uploaded sequence. 'Ambiguous' indicates "
            "that the score separation between the two highest-scoring Atlas clades does not meet "
            "the predefined classification margin."
        )
        if str(predicted_family).lower() == "ambiguous":
            fam_cls = transient_session.family_classification
            best_match = "Unknown"
            if hasattr(fam_cls, "ranked_family_scores") and fam_cls.ranked_family_scores:
                best_match = fam_cls.ranked_family_scores[0][0]
            elif hasattr(fam_cls, "best_family"):
                best_match = fam_cls.best_family
            st.markdown(f"**Atlas Family-Clade Prediction:** `Ambiguous`", help=family_help)
            st.markdown(f"**Best Matching Clade:** `{best_match}`")
        else:
            st.markdown(f"**Atlas Family-Clade Prediction:** `{predicted_family}`", help=family_help)

        st.markdown("**Reference Alignment:** `Successful`")

    with st.expander("Technical mapping details"):
        st.caption(f"Sequence Hash: {transient_session.study_sequence.sequence_hash}")
        st.caption(f"Atlas Coordinate System: {coordinate_system}")
        st.caption(f"Alignment Score: {transient_session.mapping_result.alignment_score}")
        st.caption(f"Identity Percent: {transient_session.mapping_result.identity_percent:.1f}%")

    # Authoritative Primary Workflow: Function-First Top30 WHERE + Evolutionary WHAT
    ff_hotspots = getattr(transient_session, "function_first_hotspots", [])
    if ff_hotspots:
        st.write("---")
        render_function_first_hotspots_view(ff_hotspots)

    # Legacy V2.4 Analysis Collapsed at Bottom
    render_legacy_v24_analysis(
        recommendations=recommendations,
        workspace_mode="Analyze Custom Sequence",
        transient_session=transient_session
    )