import json
import streamlit as st
import pandas as pd

from engine.residue_search import ResidueSearchEngine
from engine.family_engine import FamilyEngine
from engine.knowledge_graph_engine import KnowledgeGraphEngine
from engine.functional_hotspots import FunctionFirstEngine
from app.utils.theme import apply_custom_css

def json_default(obj):
    if hasattr(obj, "item"):
        return obj.item()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return str(obj)

st.set_page_config(
    page_title="Atlas Explorer",
    page_icon="📊",
    layout="wide",
)

apply_custom_css()

st.title("📊 Atlas Dataset Explorer")
st.caption("Master reference dataset query and position evidence hub.")

search_engine = ResidueSearchEngine()
family_engine = FamilyEngine()
knowledge_graph = KnowledgeGraphEngine()

# Precompute Function-First lookup
@st.cache_resource
def get_ff_lookup():
    ff_eng = FunctionFirstEngine()
    top30 = ff_eng.get_reference_top30()
    return {p.reference_position: p for p in top30}

ff_lookup = get_ff_lookup()

with st.sidebar:
    st.header("Search Reference Dataset")
    query = st.text_input(
        "Search Position or Residue",
        value="238",
        help="Examples: 238, S238, S238F",
    )

results = search_engine.search(query)

if not results:
    st.error(f'No reference position matches query "{query}".')
    st.stop()

result = results[0]
residue = result.payload

# Function-First Top30 Status
pos_num = getattr(residue, "position", 238)
ff_match = ff_lookup.get(pos_num, None)

st.markdown(f"### IsPETase Reference Position {pos_num} ({getattr(residue, 'reference_residue', '')})")

if ff_match:
    st.success(f"🎯 **Prioritized Engineering Position**: Rank #{ff_match.where_rank} / 30 | Priority Group: {ff_match.priority_group}")
else:
    st.info("Information: Standard reference position (not in Top30 shortlist).")

# Clean 4-tab structure
tab_over, tab_evo, tab_struct, tab_lit = st.tabs([
    "Overview",
    "Evolution",
    "Structure",
    "Literature"
])

with tab_over:
    col_o1, col_o2, col_o3 = st.columns(3)
    col_o1.metric("Reference Residue", getattr(residue, "reference_residue", "N/A"))
    col_o2.metric("Variability Level", f"FVI {getattr(residue, 'fvi', 'N/A')}")
    col_o3.metric("Global Conservation", f"{getattr(residue, 'global_conservation', 0):.1f}%")

    st.markdown("#### Primary Evidence Rationale")
    if ff_match:
        st.markdown(f"- **3D Functional Role:** {ff_match.functional_classes}")
        st.markdown(f"- **Evolutionary Permissiveness:** {ff_match.evolutionary_permissiveness}")
        st.markdown(f"- **Distance to Substrate:** {ff_match.substrate_distance:.1f} Å")
        st.markdown(f"- **Distance to Catalytic Triad:** {ff_match.catalytic_distance:.1f} Å")
    else:
        st.markdown(f"- **Global Consensus Residue:** {getattr(residue, 'global_consensus', 'N/A')}")
        st.markdown(f"- **Known Mutations:** {getattr(residue, 'known_mutations', 'None')}")

with tab_evo:
    st.subheader("Evolutionary Variability & Family Consensus")
    family_data = family_engine.get_position_family_consensus(pos_num)
    if family_data:
        rows = []
        for fam, val in family_data.items():
            if val.get("consensus"):
                rows.append({
                    "Subfamily": fam,
                    "Consensus Residue": val.get("consensus"),
                    "Conservation (%)": f"{val.get('conservation', 0):.1f}%",
                    "Sequence Count": val.get("nseq", 0)
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No subfamily consensus profile available for this position.")

with tab_struct:
    st.subheader("Reference Structural Context")
    if ff_match:
        c_s1, c_s2 = st.columns(2)
        c_s1.metric("Distance to Substrate (HEMT)", f"{ff_match.substrate_distance:.1f} Å")
        c_s2.metric("Distance to Catalytic Triad", f"{ff_match.catalytic_distance:.1f} Å")
        st.metric("Relative SASA Exposure", f"{ff_match.relative_sasa:.2f}")
    else:
        st.info("Reference structural annotations available for Function-First positions.")

with tab_lit:
    st.subheader("Published Literature Evidence")
    context = knowledge_graph.get_residue_context(pos_num)
    known = getattr(residue, "known_mutations", None)
    if known:
        st.markdown(f"**Published Mutations:** `{known}`")
        st.caption("Note: Published literature annotations are displayed for scientific reference and do NOT alter predictions.")
    else:
        st.info("No published experimental mutations reported for this position in literature.")

with st.expander("Advanced Technical Export"):
    context = knowledge_graph.get_residue_context(pos_num)
    st.download_button(
        label="Download position context as JSON",
        data=json.dumps(context.to_dict(), indent=2, default=json_default),
        file_name=f"reference_position_{pos_num}_context.json",
        mime="application/json",
    )