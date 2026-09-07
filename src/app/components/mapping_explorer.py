import streamlit as st
import pandas as pd
from engine.mapping_status import MappingStatus
from engine.family_engine import FamilyEngine

class MappingExplorerViewModel:
    """
    Transforms the coordinate mapping data into UI-ready rows
    for display in the mapping explorer table.
    """
    @staticmethod
    def build_rows(mapping_result, recommendations, predicted_family: str) -> list[dict]:
        rows = []
        fam_engine = FamilyEngine()

        # Build lookup for recommendations by Atlas Position
        rec_by_atlas = {}
        for rec in recommendations:
            ap = rec.get("atlas_position")
            if ap is not None:
                rec_by_atlas[int(ap)] = rec

        for mr in mapping_result.mapped_residues:
            status_enum = mr.mapping_status
            
            # Map status label override
            if status_enum == MappingStatus.EXACT_MATCH:
                status_label = "Aligned"
            elif status_enum == MappingStatus.SUBSTITUTION:
                status_label = "Substitution"
            elif status_enum == MappingStatus.INSERTION:
                status_label = "Insertion"
            elif status_enum == MappingStatus.DELETION:
                status_label = "Deletion"
            else:
                status_label = "Unmapped"

            atlas_pos = mr.atlas_position_id
            atlas_res = mr.atlas_reference_residue
            query_pos = mr.study_position
            query_res = mr.study_residue

            # Format coordinates string values or fallback to "—"
            atlas_pos_str = str(atlas_pos) if atlas_pos is not None else "—"
            atlas_res_str = str(atlas_res) if atlas_res is not None else "—"
            query_pos_str = str(query_pos) if query_pos is not None else "—"
            query_res_str = str(query_res) if query_res is not None else "—"

            atlas_label = f"{atlas_res}{atlas_pos}" if (atlas_pos is not None and atlas_res) else "—"
            query_label = f"{query_res}{query_pos}" if (query_pos is not None and query_res) else "—"

            # Retrieve Atlas-level properties
            global_conservation = "—"
            fvi_val = "—"
            atlas_score = "—"
            known_mutations = "—"
            consensus_residues = "—"
            family_conservation = "—"

            if mr.atlas_position is not None:
                ap_obj = mr.atlas_position
                global_conservation = f"{int(ap_obj.global_conservation)}%" if ap_obj.global_conservation is not None else "—"
                fvi_val = str(ap_obj.fvi) if ap_obj.fvi is not None else "—"
                atlas_score = str(ap_obj.atlas_evidence_score) if ap_obj.atlas_evidence_score is not None else "—"
                
                # Format known mutations list
                km = ap_obj.known_mutations
                if km:
                    if isinstance(km, list):
                        known_mutations = ", ".join([str(x) for x in km])
                    else:
                        known_mutations = str(km)
                
                # Format consensus
                cr = ap_obj.consensus_residues
                if cr:
                    consensus_residues = " ".join(cr) if isinstance(cr, list) else str(cr)

                # Look up family conservation via FamilyEngine
                try:
                    pos_data = fam_engine.get_position_family_consensus(atlas_pos)
                    if predicted_family in pos_data:
                        cons_data = pos_data[predicted_family]
                        if cons_data.get("conservation") is not None:
                            family_conservation = f"{int(cons_data['conservation'])}%"
                except Exception:
                    pass

            # Recommendation status lookup
            has_rec = "No"
            if atlas_pos is not None and int(atlas_pos) in rec_by_atlas:
                has_rec = "Yes"

            rows.append({
                "Mapping Status": status_label,
                "Atlas Position": atlas_pos_str,
                "Atlas Residue": atlas_res_str,
                "Query Position": query_pos_str,
                "Query Residue": query_res_str,
                "Atlas Label": atlas_label,
                "Query Label": query_label,
                "Global Conservation": global_conservation,
                "Family Conservation": family_conservation,
                "FVI": fvi_val,
                "Atlas Evidence Score": atlas_score,
                "Known Mutations": known_mutations,
                "Consensus Residues": consensus_residues,
                "Recommended Mutation Available": has_rec
            })

        return rows


def render_mapping_explorer(mapping_result, recommendations, predicted_family: str) -> None:
    """
    Renders the Coordinate Mapping Explorer layout: Filters -> Alignment Table -> Details Panel.
    Receives only computed data. Does not run alignments or fetch repositories.
    """
    if mapping_result is None or not hasattr(mapping_result, "mapped_residues"):
        st.info("No sequence coordinate mapping context available.")
        return

    # Transform data using ViewModel helper
    rows = MappingExplorerViewModel.build_rows(
        mapping_result=mapping_result,
        recommendations=recommendations,
        predicted_family=predicted_family
    )

    if not rows:
        st.caption("Alignment mapping contains no residues.")
        return

    st.markdown("### 🔀 Coordinate Mapping Registry")
    
    # 1. Filters Row
    col_ft1, col_ft2, col_ft3, col_ft4 = st.columns(4)
    with col_ft1:
        status_filter = st.multiselect(
            "Filter by Mapping Status",
            options=["Aligned", "Substitution", "Insertion", "Deletion"],
            default=["Aligned", "Substitution", "Insertion", "Deletion"]
        )
    with col_ft2:
        search_atlas = st.text_input("Search Atlas Position (e.g. 121)", value="")
    with col_ft3:
        search_query = st.text_input("Search Query Position (e.g. 96)", value="")
    with col_ft4:
        recs_only = st.checkbox("Only residues with recommendations", value=False)

    # Apply filters
    filtered_rows = []
    for r in rows:
        if r["Mapping Status"] not in status_filter:
            continue
        if search_atlas and search_atlas not in r["Atlas Position"]:
            continue
        if search_query and search_query not in r["Query Position"]:
            continue
        if recs_only and r["Recommended Mutation Available"] != "Yes":
            continue
        filtered_rows.append(r)

    if not filtered_rows:
        st.warning("No coordinate maps match the current search filters.")
        return

    # 2. Render Table Grid
    st.dataframe(pd.DataFrame(filtered_rows), use_container_width=True, hide_index=True)

    # 3. Residue Detail Inspection Panel
    st.write("---")
    st.markdown("### 🔍 Residue Inspection Profile")
    
    inspect_options = []
    inspect_map = {}
    for r in filtered_rows:
        lbl = f"Query: {r['Query Label']} → Atlas: {r['Atlas Label']} ({r['Mapping Status']})"
        inspect_options.append(lbl)
        inspect_map[lbl] = r

    selected_lbl = st.selectbox(
        "Select a residue mapping to inspect details:",
        options=inspect_options,
        key="mapping_explorer_inspect_select"
    )
    
    if selected_lbl:
        row = inspect_map[selected_lbl]
        
        col_q, col_a, col_e = st.columns(3)
        with col_q:
            st.markdown("##### Query sequence coordinate")
            st.metric("Query Position", row["Query Position"])
            st.metric("Query Residue", row["Query Residue"])
            
        with col_a:
            st.markdown("##### Atlas reference coordinate")
            st.metric("Atlas Position", row["Atlas Position"])
            st.metric("Atlas Residue", row["Atlas Residue"])
            st.markdown(f"**Mapping Status:** `{row['Mapping Status']}`")
            
        with col_e:
            st.markdown("##### Evolutionary evidence")
            st.metric("Predicted Family Clade", predicted_family)
            st.metric("Global Conservation", row["Global Conservation"])
            st.metric("Family Conservation", row["Family Conservation"])
            
        col_e1, col_e2, col_ev_extra = st.columns(3)
        with col_e1:
            st.metric("FVI Score", row["FVI"])
            st.metric("Atlas Evidence Score", row["Atlas Evidence Score"])
        with col_e2:
            st.write(f"**Global Consensus Residue:** `{row['Consensus Residues']}`")
            st.write(f"**Known literature mutations:** `{row['Known Mutations']}`")
        with col_ev_extra:
            atlas_id_str = row["Atlas Position"]
            if atlas_id_str != "—":
                try:
                    from engine.residue import Residue
                    res_obj = Residue(int(atlas_id_str))
                    fam_consensus = res_obj.family_consensus
                    if fam_consensus:
                        st.markdown("**Clade Consensus Residues:**")
                        st.dataframe(
                            pd.DataFrame(list(fam_consensus.items()), columns=["Clade", "Consensus Residue"]),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.caption("No clade consensus available.")
                except Exception:
                    st.caption("Clade consensus lookup failed.")
            else:
                st.caption("No Atlas coordinate associated.")

        # Engineering recommendation section
        st.write("---")
        st.markdown("##### Engineering recommendations")
        if row["Recommended Mutation Available"] == "Yes" and row["Atlas Position"] != "—":
            atlas_pos_int = int(row["Atlas Position"])
            rec = next((r for r in recommendations if r.get("atlas_position") == atlas_pos_int), None)
            if rec:
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.metric("Query mutation notation", rec.get("project_mutation_label") or "—")
                    st.metric("Atlas mutation notation", rec.get("atlas_mutation_label") or "—")
                with col_r2:
                    st.metric("Recommendation Score", rec.get("proposal_score", "—"))
                    st.metric("Recommendation Priority", rec.get("proposal_priority", "—"))
                
                # Evidence explanation
                explanation = rec.get("evidence_explanation", {})
                st.markdown("**Evidence Interpretation:**")
                st.info(explanation.get("final_interpretation") or rec.get("interpretation", "No interpretation text available."))
        else:
            st.caption("No engineering recommendation matches this position.")
