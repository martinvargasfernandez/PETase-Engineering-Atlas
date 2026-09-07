import streamlit as st


def render_candidate_card(report, selected=False):

    best = report.best_mutation

    score = report.atlas_evidence_score

    if score >= 8:
        color = "🟢"
    elif score >= 5:
        color = "🟡"
    else:
        color = "⚪"

    title = f"{color} Position {report.position}"

    if selected:
        title += "   ✓"

    with st.container(border=True):

        st.markdown(f"### {title}")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.caption("Best proposal")
            st.write(best.label if best else "-")

        with col2:
            st.caption("Atlas score")
            st.write(report.atlas_evidence_score)

        st.caption("Priority")
        st.write(report.priority)