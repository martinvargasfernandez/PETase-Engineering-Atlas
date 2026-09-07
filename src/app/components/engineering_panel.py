import streamlit as st
import pandas as pd


def render_engineering_panel(report):

    st.subheader("Engineering Proposals")

    best = report.best_mutation

    if best is None:
        st.info("No engineering proposals available.")
        return

    st.markdown("### Best Proposal")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Mutation", best.label)
    c2.metric("Score", best.proposal_score)
    c3.metric("Priority", best.proposal_priority)
    c4.metric("Chemical Change", best.chemical_change())

    st.markdown("#### Sources")

    for source in best.sources:
        st.write(f"• {source}")

    st.markdown("#### Score Components")

    components = best.evidence.get("proposal_score_components", {})

    if components:
        rows = [
            {"Component": key, "Value": value}
            for key, value in components.items()
        ]

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No score components available.")

    st.divider()

    st.markdown("### Alternative Proposals")

    if not report.alternative_mutations:
        st.info("No alternative proposals.")
        return

    rows = []

    for mutation in report.alternative_mutations:
        rows.append(
            {
                "Mutation": mutation.label,
                "Score": mutation.proposal_score,
                "Priority": mutation.proposal_priority,
                "Sources": ", ".join(mutation.sources),
                "Chemical Change": mutation.chemical_change(),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )