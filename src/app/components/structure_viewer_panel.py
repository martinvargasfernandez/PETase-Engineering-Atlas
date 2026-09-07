import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from app.components.structure_viewer import (
    load_local_3dmol_javascript,
    load_validated_pdb_text,
    build_structure_viewer_html
)

VIEWER_COLORS = {
    "protein": "#E0E0E0",      # Neutral light-grey cartoon backbone
    "target": "#FF4B4B",       # Actionable red sticks for target residue
    "ligand": "#00D2C4",       # Teal sticks for the PET ligand
    "catalytic": "#FFAA00",    # Gold/orange sticks for core catalytic residues
    "background": "#1E1E1E"    # Deep charcoal background for WebGL viewport
}

def render_structure_viewer_panel(
    selected_rec: dict,
    active_cs_list: list,
    project,
    cs_repo,
    eng_engine,
    js_path: Path
) -> None:
    if not selected_rec:
        st.info("No recommendation selected.")
        return
        
    if not active_cs_list:
        st.warning("No active Case Study computational profile loaded for this project. 3D Structure Viewer is disabled.")
        return
        
    try:
        cs_summary = active_cs_list[0]
        case_study_id = cs_summary.get("case_study_id")
        active_cs = cs_repo.load_case_study(project, case_study_id)
    except Exception as e:
        st.error(f"Failed to load active case study: {str(e)}")
        return

    try:
        context = eng_engine.build_structure_viewer_context(
            selected_rec,
            active_cs,
            project.primary_study_sequence
        )
    except Exception as e:
        st.error(f"Failed to compile structure context: {str(e)}")
        return

    # 2. Check structure availability fallback
    if not context.structure_available:
        st.warning(context.viewer_message or "No representative structure available.")
        return

    # 3. Resolve path safely
    try:
        resolved_path = cs_repo.resolve_representative_structure_path(project, case_study_id)
        sanitized_filename = resolved_path.name
    except FileNotFoundError as e:
        rel_path = active_cs.representative_structure.relative_path if active_cs.representative_structure else "unknown"
        sanitized_rel_path = Path(rel_path).name
        st.error(f"Representative structure file not found: {sanitized_rel_path}")
        return
    except ValueError as e:
        st.warning(str(e))
        return
    except Exception as e:
        st.error(f"Structure path resolution failed: {str(e)}")
        return

    # 4. Load PDB text
    try:
        pdb_text = load_validated_pdb_text(resolved_path)
    except ValueError as e:
        st.warning(str(e))
        return
    except Exception as e:
        st.error(f"Failed to load PDB content: {str(e)}")
        return

    # 5. Load JavaScript asset
    try:
        js_text = load_local_3dmol_javascript(js_path)
    except FileNotFoundError as e:
        st.error("Local 3Dmol.js visual library asset is missing in the workspace. Viewer bypassed.")
        return
    except Exception as e:
        st.error(f"Failed to load javascript library: {str(e)}")
        return

    # 6. Build HTML
    try:
        html = build_structure_viewer_html(
            context,
            pdb_text,
            js_text,
            colors=VIEWER_COLORS
        )
    except Exception as e:
        st.error(f"HTML compiler exception: {str(e)}")
        return

    # 7. Render Streamlit components
    st.markdown("### 3D Structure")
    st.caption(f"Representative structure file: `{sanitized_filename}`")
    
    # Display mapping alerts
    if context.structure_mapping_status == "residue_mismatch":
        st.warning(context.viewer_message)
    elif context.structure_mapping_status == "mapped":
        st.success(f"Successfully mapped study residue {context.study_current_residue}{context.study_position} to PDB Chain {context.protein_chain} residue {context.pdb_residue_name}{context.pdb_residue_number}.")
    else:
        st.info(context.viewer_message)
        
    components.html(html, height=500, scrolling=False)
    st.caption("Interactive 3D representation. Red: target residue, Teal: PET ligand. Rotate with left click, zoom with scroll/right click.")
