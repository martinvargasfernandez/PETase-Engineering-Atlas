import streamlit as st


def render_residue_overview(report):

    st.header(f"Residue {report.position} ({report.reference_residue})")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Atlas Evidence Score",
        report.atlas_evidence_score,
    )

    c2.metric(
        "Atlas Priority",
        report.priority,
    )

    c3.metric(
        "Alternative Proposals",
        len(report.alternative_mutations),
    )

    st.divider()

    best = report.best_mutation

    st.subheader("Best Engineering Proposal")

    if best is None:
        st.info("No proposal available.")
        return

    b1, b2, b3 = st.columns(3)

    b1.metric(
        "Mutation",
        best.label,
    )

    b2.metric(
        "Proposal Score",
        best.proposal_score,
    )

    b3.metric(
        "Priority",
        best.proposal_priority,
    )

    st.markdown("#### Sources")

    for source in best.sources:
        st.write(f"• {source}")