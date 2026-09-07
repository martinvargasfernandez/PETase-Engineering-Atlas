import streamlit as st


def render_atlas_panel(report):

    residue = report.residue

    st.subheader("Atlas Evidence")

    c1, c2, c3 = st.columns(3)

    c1.metric("FVI", residue.fvi)
    c2.metric("Global Conservation", residue.global_conservation)
    c3.metric("Atlas Score", report.atlas_evidence_score)

    st.markdown("### Family Consensus")

    family_consensus = residue.family_consensus

    if family_consensus:

        rows = []

        for family, aa in family_consensus.items():

            rows.append(
                {
                    "Family": family,
                    "Consensus": aa,
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No family consensus available.")

    st.markdown("### Known Mutations")

    if residue.known_mutations:
        st.write(residue.known_mutations)
    else:
        st.info("No known mutations registered.")

    st.markdown("### Interpretation")

    st.write(report.interpretation)