import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from engine.atlas import get_atlas_summary, load_master_table
from engine.families import get_family_summary
from app.utils.theme import apply_custom_css

st.set_page_config(
    page_title="PETase Engineering Atlas",
    page_icon="🧬",
    layout="wide",
)

apply_custom_css()

st.title("🧬 PETase Engineering Atlas")
st.caption("Computational platform for PETase engineering position discovery, substitution proposal, and evidence interpretation.")

st.markdown("---")

# 3 Conceptual Cards Layout
st.markdown("### The Core Engineering Workflow")
c_where, c_what, c_why = st.columns(3)

with c_where:
    st.markdown("""
    <div style="background-color: #111827; border: 1px solid #14B8A6; border-radius: 8px; padding: 18px;">
        <h4 style="color: #14B8A6; margin-top:0;">🎯 1. WHERE</h4>
        <p style="color: #F8FAFC; font-size: 0.95rem;"><b>Candidate Engineering Positions</b></p>
        <p style="color: #94A3B8; font-size: 0.85rem;">Prioritizes positions using 3D substrate cleft geometry, catalytic environment, loop accessibility, and structural stability.</p>
    </div>
    """, unsafe_allow_html=True)

with c_what:
    st.markdown("""
    <div style="background-color: #111827; border: 1px solid #38BDF8; border-radius: 8px; padding: 18px;">
        <h4 style="color: #38BDF8; margin-top:0;">💡 2. WHAT</h4>
        <p style="color: #F8FAFC; font-size: 0.95rem;"><b>Suggested Substitutions</b></p>
        <p style="color: #94A3B8; font-size: 0.85rem;">Proposes evolution-supported amino-acid substitutions derived from PETase family consensus frequencies.</p>
    </div>
    """, unsafe_allow_html=True)

with c_why:
    st.markdown("""
    <div style="background-color: #111827; border: 1px solid #22C55E; border-radius: 8px; padding: 18px;">
        <h4 style="color: #22C55E; margin-top:0;">🔬 3. WHY</h4>
        <p style="color: #F8FAFC; font-size: 0.95rem;"><b>Supporting Evidence</b></p>
        <p style="color: #94A3B8; font-size: 0.85rem;">Provides 3D structural rationale, evolutionary permissiveness, and published literature annotations.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
col_action, _ = st.columns([2, 3])
with col_action:
    st.page_link("pages/Engineering_Workspace.py", label="🧬 Analyze a PETase Sequence →", use_container_width=True)

st.markdown("---")

# Technical Dataset Context (Collapsible)
with st.expander("Atlas Platform Overview & Master Dataset Metrics"):
    summary = get_atlas_summary()
    family_summary = get_family_summary()
    master = load_master_table()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reference Positions", summary["reference_positions"])
    c2.metric("Protein Sequences", int(family_summary["sequence_count"].sum()))
    c3.metric("Evolutionary Families", len(family_summary))
    c4.metric("High-Variability Sites", summary["high_fvi_positions"])

    left, right = st.columns(2)
    with left:
        st.subheader("Family Composition")
        st.bar_chart(family_summary.set_index("family_name")["sequence_count"])
    with right:
        st.subheader("Variability (FVI) Distribution")
        fvi_counts = master["FVI"].value_counts().sort_index().reset_index()
        fvi_counts.columns = ["FVI", "Position Count"]
        st.bar_chart(fvi_counts.set_index("FVI")["Position Count"])