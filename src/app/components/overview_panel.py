import streamlit as st


def render_overview_panel(report):

    residue = report.residue
    best = report.best_mutation

    st.header(f"Residue {report.position} ({report.reference_residue})")

    st.caption(
        "Reference residue in the current PETase Engineering Atlas."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Atlas Score",
        report.atlas_evidence_score,
    )

    c2.metric(
        "Priority",
        report.priority,
    )

    c3.metric(
        "FVI",
        residue.fvi,
    )

    c4.metric(
        "Conservation",
        residue.global_conservation,
    )

    st.divider()

    left, right = st.columns([1, 1])

    with left:

        st.subheader("Reference")

        st.write(f"**Position:** {report.position}")
        st.write(f"**Residue:** {report.reference_residue}")

        if best:
            st.write(f"**Best proposal:** {best.label}")

    with right:

        st.subheader("Engineering Summary")

        if best:

            st.write(f"**Proposal score:** {best.proposal_score}")
            st.write(f"**Proposal priority:** {best.proposal_priority}")
            st.write(f"**Alternative mutations:** {len(report.alternative_mutations)}")

    st.divider()

    st.subheader("Scientific Summary")

    st.write(report.interpretation)