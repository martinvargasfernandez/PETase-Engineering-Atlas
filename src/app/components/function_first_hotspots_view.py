"""
Streamlit UI Component: Prioritized Engineering Positions View (Function-First WHERE + Evolutionary WHAT)

Renders the validated Function-First Top30 shortlist and detailed inspection panels
following the WHERE -> WHAT -> WHY conceptual hierarchy.

Features:
- Level 1: Compact Top10 default table with expander to show all 30.
- Level 2: Selected position inspection (Why Prioritized, Suggested Substitutions, Supporting Evidence).
- Level 3: Advanced technical details expander.
- Contextual UI principle: Hides unavailable simulation/case study sections cleanly.
"""

import streamlit as st
import pandas as pd


def translate_functional_classes_short(classes_str: str) -> str:
    """
    Translates internal Class A/B/C/D labels into concise biological functional role labels
    for the primary Top30 tables.
    """
    if not classes_str or classes_str in ("NONE", "None", "-"):
        return "Structural"

    c_upper = str(classes_str).upper()
    tokens = [t.strip() for t in c_upper.replace("CLASS_", "").split("+")]
    labels = []
    if "A" in tokens or "CLASS_A" in tokens:
        labels.append("Substrate cleft")
    if "B" in tokens or "CLASS_B" in tokens:
        labels.append("Catalytic")
    if "C" in tokens or "CLASS_C" in tokens:
        labels.append("Loop")
    if "D" in tokens or "CLASS_D" in tokens:
        labels.append("Structural")

    return " · ".join(labels) if labels else str(classes_str)


def translate_functional_classes(classes_str: str) -> str:
    """Translates internal Class A/B/C/D labels into full biological functional role descriptions."""
    if not classes_str or classes_str in ("NONE", "None", "-"):
        return "General Structural Region"

    c_upper = str(classes_str).upper()
    tokens = [t.strip() for t in c_upper.replace("CLASS_", "").split("+")]
    labels = []
    if "A" in tokens or "CLASS_A" in tokens:
        labels.append("Substrate-binding cleft")
    if "B" in tokens or "CLASS_B" in tokens:
        labels.append("Catalytic environment")
    if "C" in tokens or "CLASS_C" in tokens:
        labels.append("Accessible loop")
    if "D" in tokens or "CLASS_D" in tokens:
        labels.append("Structural context")

    return " · ".join(labels) if labels else str(classes_str)


def translate_permissiveness(perm_str: str, full_description: bool = False) -> str:
    """Translates raw permissiveness labels into user-interpretable evolutionary variability descriptions."""
    if not perm_str or perm_str in ("None", "-"):
        return "Standard"

    p_upper = str(perm_str).upper()
    if "HIGH" in p_upper or "TIER_1" in p_upper or "TIER_2" in p_upper:
        if full_description:
            return "High variability — substantial evolutionary substitution diversity is observed."
        return "High variability ●"
    elif "MODERATE" in p_upper or "TIER_3" in p_upper:
        if full_description:
            return "Moderate variability — some evolutionary substitution tolerance is observed."
        return "Moderate variability ●"
    elif "LOW" in p_upper:
        if full_description:
            return "Low variability — substitutions should be considered cautiously."
        return "Low variability ●"
    elif "CONSERVED" in p_upper or "TIER_4" in p_upper:
        if full_description:
            return "Conserved — substitutions require strong supporting evidence."
        return "Conserved ●"
    else:
        return f"{perm_str} ●" if not full_description else str(perm_str)


def generate_evidence_summary(raw_classes: str, raw_perm: str) -> str:
    """
    Generates a deterministic human-readable evidence summary from existing functional classes and permissiveness.
    Does NOT introduce new scientific claims, causal claims, activity predictions, or use LLM/inference.
    """
    c_upper = str(raw_classes or "").upper()
    tokens = [t.strip() for t in c_upper.replace("CLASS_", "").split("+")]
    has_a = "A" in tokens or "CLASS_A" in tokens
    has_b = "B" in tokens or "CLASS_B" in tokens
    has_c = "C" in tokens or "CLASS_C" in tokens
    has_d = "D" in tokens or "CLASS_D" in tokens

    role_parts = []
    if has_a:
        role_parts.append("in the substrate-binding cleft")
    if has_b:
        role_parts.append("near the catalytic environment")
    if has_c:
        role_parts.append("in an accessible structural region")
    if has_d:
        role_parts.append("in a buried structural packing region")

    if len(role_parts) >= 2:
        roles_text = " and ".join([", ".join(role_parts[:-1]), role_parts[-1]]) if len(role_parts) > 2 else " and ".join(role_parts)
        func_desc = f"This position lies {roles_text}."
    elif len(role_parts) == 1:
        func_desc = f"This position lies {role_parts[0]}."
    else:
        func_desc = "This position satisfies structural prioritization criteria."

    p_upper = str(raw_perm or "").upper()
    if "HIGH" in p_upper or "TIER_1" in p_upper or "TIER_2" in p_upper:
        perm_desc = "Its high evolutionary variability indicates substantial sequence diversity across homologs."
    elif "MODERATE" in p_upper or "TIER_3" in p_upper:
        perm_desc = "Its moderate evolutionary variability indicates some evolutionary substitution tolerance."
    elif "LOW" in p_upper:
        perm_desc = "Its low evolutionary variability suggests that substitutions should be evaluated cautiously."
    elif "CONSERVED" in p_upper or "TIER_4" in p_upper:
        perm_desc = "Its high sequence conservation suggests structural constraints, requiring strong supporting evidence for mutation."
    else:
        perm_desc = "Substitutions should be evaluated with care based on evolutionary evidence."

    return f"{func_desc} {perm_desc}"


def render_function_first_hotspots_view(function_first_hotspots: list):
    """
    Renders the Prioritized Engineering Positions workflow (WHERE -> WHAT -> WHY).
    """
    st.subheader("🎯 Prioritized Engineering Positions")
    st.caption(
        "Function-first shortlist of mapped candidate engineering positions. "
        "Substitutions are prioritized using evolutionary evidence."
    )

    if not function_first_hotspots:
        st.info("No prioritized engineering position data available.")
        return

    # Process items into standard format
    processed = []
    for item in function_first_hotspots:
        if isinstance(item, dict):
            rk = item.get("where_rank")
            q_pos = item.get("query_position")
            q_wt = item.get("query_residue")
            ref_pos = item.get("reference_position")
            ref_wt = item.get("reference_residue")
            grp = item.get("priority_group")
            cls_raw = item.get("functional_classes")
            perm_raw = item.get("evolutionary_permissiveness")
            status = item.get("recommendation_status")
            subs = item.get("substitutions", [])
            expl = item.get("where_explanation")
            d_sub = item.get("substrate_distance", 99.0)
            d_cat = item.get("catalytic_distance", 99.0)
            sasa = item.get("relative_sasa", 0.0)
        else:
            rk = getattr(item, "where_rank", None)
            q_pos = getattr(item, "query_position", None)
            q_wt = getattr(item, "query_residue", None)
            ref_pos = getattr(item, "reference_position", None)
            ref_wt = getattr(item, "reference_residue", None)
            grp = getattr(item, "priority_group", None)
            cls_raw = getattr(item, "functional_classes", None)
            perm_raw = getattr(item, "evolutionary_permissiveness", None)
            status = getattr(item, "recommendation_status", None)
            subs = getattr(item, "substitutions", [])
            expl = getattr(item, "where_explanation", None)
            d_sub = getattr(item, "substrate_distance", 99.0)
            d_cat = getattr(item, "catalytic_distance", 99.0)
            sasa = getattr(item, "relative_sasa", 0.0)

        func_role_short = translate_functional_classes_short(cls_raw)
        func_role_full = translate_functional_classes(cls_raw)
        perm = translate_permissiveness(perm_raw, full_description=False)
        perm_full = translate_permissiveness(perm_raw, full_description=True)

        if subs:
            top_subs_list = [f"{s.candidate_residue if hasattr(s, 'candidate_residue') else s.get('candidate_residue')}" for s in subs[:3]]
            top_subs_str = ", ".join(top_subs_list)
        else:
            top_subs_str = "None (Protected)" if "PROTECTED" in str(status) else "-"

        q_str = f"{q_wt}{q_pos}" if q_pos is not None else f"Unmapped (Ref: {ref_wt}{ref_pos})"

        # User-facing status clarification: RECOMMENDED -> PRIORITIZED
        if "RECOMMENDED" in str(status):
            display_status = "Prioritized Candidate"
        elif "PROTECTED" in str(status):
            display_status = "Protected Residue"
        else:
            display_status = str(status)

        processed.append({
            "Position Priority Rank": rk,
            "Query Position": q_str,
            "Reference Position": f"{ref_wt}{ref_pos}",
            "Functional Role": func_role_short,
            "Functional Role Full": func_role_full,
            "Evolutionary Variability": perm,
            "Evolutionary Variability Full": perm_full,
            "Suggested Substitutions": top_subs_str,
            "Status": display_status,
            "raw_classes": cls_raw,
            "raw_perm": perm_raw,
            "raw_status": status,
            "group": grp,
            "substitutions": subs,
            "explanation": expl,
            "substrate_distance": d_sub,
            "catalytic_distance": d_cat,
            "sasa": sasa,
            "q_pos": q_pos,
            "q_wt": q_wt,
            "ref_pos": ref_pos,
            "ref_wt": ref_wt,
            "Rank": rk
        })

    df_all = pd.DataFrame(processed)

    st.caption(
        "💡 **Position Priority Rank:** Position Priority Rank orders positions within the validated "
        "Function-First Top30 shortlist. Rank #1 indicates the highest-priority position for engineering exploration; "
        "it is not a predicted probability of beneficial activity."
    )

    primary_cols = ["Position Priority Rank", "Query Position", "Reference Position", "Functional Role", "Evolutionary Variability", "Suggested Substitutions"]

    # Display Top 10 by default
    df_top10 = df_all.iloc[:10][primary_cols]
    st.dataframe(df_top10, use_container_width=True, hide_index=True)

    # Expander for full Top30
    if len(processed) > 10:
        with st.expander(f"Show all {len(processed)} prioritized positions"):
            df_full = df_all[primary_cols]
            st.dataframe(df_full, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # LEVEL 2: SELECTED POSITION INSPECTION (WHERE -> WHAT -> WHY)
    # -------------------------------------------------------------
    st.write("---")
    st.markdown("### 🔬 Inspect Selected Engineering Position")

    pos_options = [f"Rank #{p['Rank']}: {p['Query Position']} (Ref: {p['Reference Position']})" for p in processed]
    selected_idx = st.selectbox("Select position to inspect", range(len(pos_options)), format_func=lambda i: pos_options[i])
    
    sel = processed[selected_idx]

    # Position Summary Banner
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.metric("Position Priority Rank", f"#{sel['Rank']} of 30")
    with col_b2:
        st.metric("Query Position", sel["Query Position"])
    with col_b3:
        st.metric("Reference Position", sel["Reference Position"])
    with col_b4:
        if "Protected" in str(sel["Status"]) or "PROTECTED" in str(sel["raw_status"]):
            st.error("Status: Protected Catalytic Residue ●")
        elif sel["q_pos"] is None:
            st.warning(f"Status: {sel['Status']} ●")
        else:
            st.success("Status: Prioritized Candidate ●")

    # Section 1: WHY THIS POSITION IS PRIORITIZED
    st.markdown("#### 1. Why this position is prioritized (WHERE)")
    with st.container(border=True):
        st.markdown(f"**Functional Context:** {sel['Functional Role Full']}")
        st.markdown(f"**Evolutionary Variability:** {sel['Evolutionary Variability Full']}")
        summary_text = generate_evidence_summary(sel["raw_classes"], sel["raw_perm"])
        st.info(f"💡 **Evidence Summary:** {summary_text}")

    # Section 2: WHAT SHOULD I SUBSTITUTE?
    st.markdown("#### 2. Suggested Substitutions (WHAT)")
    st.caption(
        "💡 **Atlas-wide evolutionary support:** Suggested substitutions are ranked by amino-acid occurrence "
        "at the mapped reference position across the 628-sequence PETase alignment, excluding the uploaded sequence's current residue."
    )
    subs = sel["substitutions"]
    if subs:
        sub_rows = []
        for s in subs:
            aa = s.candidate_residue if hasattr(s, "candidate_residue") else s.get("candidate_residue")
            rk_evo = s.evolutionary_rank if hasattr(s, "evolutionary_rank") else s.get("evolutionary_rank")
            cnt = s.msa_count if hasattr(s, "msa_count") else s.get("msa_count")
            q_mut = f"{sel['q_wt']}{sel['q_pos']}{aa}" if sel['q_pos'] is not None else f"{sel['ref_wt']}{sel['ref_pos']}{aa}"
            sub_rows.append({
                "Rank": f"#{rk_evo}",
                "Suggested Substitution": q_mut,
                "Candidate Amino Acid": aa,
                "MSA Sequence Count": f"{cnt} sequences"
            })
        st.dataframe(pd.DataFrame(sub_rows), use_container_width=True, hide_index=True)
    else:
        st.warning("No mutation proposals available for this position (Protected Catalytic / Disulfide).")

    # Section 3: SUPPORTING EVIDENCE
    st.markdown("#### 3. Supporting Evidence")
    with st.container(border=True):
        st.caption(
            "💡 **Reference structural context:** Structural annotations below are transferred from the mapped IsPETase "
            "reference structure (PDB 6EQE); they are not calculated directly from a 3D structure of the uploaded sequence."
        )
        st.markdown(f"- Reference substrate proximity: **{sel['substrate_distance']:.1f} Å**")
        st.markdown(f"- Reference catalytic-environment proximity: **{sel['catalytic_distance']:.1f} Å**")
        st.markdown(f"- Reference relative surface exposure (SASA): **{sel['sasa']:.2f}**")

    # Section 4: ADVANCED TECHNICAL DETAILS (LEVEL 3)
    with st.expander("Technical details (Advanced)"):
        st.json({
            "shortlist_rank": sel["Rank"],
            "query_position": sel["q_pos"],
            "query_residue": sel["q_wt"],
            "reference_position": sel["ref_pos"],
            "reference_residue": sel["ref_wt"],
            "priority_group": sel["group"],
            "functional_classes_raw": sel["raw_classes"],
            "permissiveness_raw": sel["raw_perm"],
            "substrate_distance_angstroms": sel["substrate_distance"],
            "catalytic_distance_angstroms": sel["catalytic_distance"],
            "relative_sasa": sel["sasa"],
            "internal_recommendation_status": str(sel["raw_status"])
        })
