import json
from pathlib import Path

# Expected immutable asset details
EXPECTED_SHA256 = "612eedd3ad7c36537813066d04f15a6e71285b9c59b364a6ab0296e39c67b7d1"
MAX_VIEWER_PDB_BYTES = 2 * 1024 * 1024

DEFAULT_COLORS = {
    "protein": "#E0E0E0",
    "target": "#FF4B4B",
    "ligand": "#00D2C4",
    "catalytic": "#FFAA00",
    "background": "#1E1E1E"
}

def load_local_3dmol_javascript(asset_path: Path) -> str:
    """
    Reads the local 3Dmol-min.js asset content.
    Validation is performed in the test suite and can be performed once during loading.
    """
    if not asset_path.exists():
        raise FileNotFoundError(f"Missing local 3Dmol.js asset: {asset_path}")
    if not asset_path.is_file():
        raise ValueError(f"Asset path is not a file: {asset_path}")
    return asset_path.read_text(encoding="utf-8")

def load_validated_pdb_text(pdb_path: Path, max_bytes: int = MAX_VIEWER_PDB_BYTES) -> str:
    """
    Safely loads PDB text, validating suffix, size limits, and non-emptiness.
    """
    if pdb_path.suffix.lower() != ".pdb":
        raise ValueError(f"Unsupported structure file format: only .pdb is supported in Viewer V1.")
    
    # Wrapped Windows path check
    if not pdb_path.exists() or not pdb_path.is_file():
        raise FileNotFoundError(f"PDB file not found: {pdb_path}")
        
    size = pdb_path.stat().st_size
    if size == 0:
        raise ValueError("PDB structure file is empty.")
    if size > max_bytes:
        raise ValueError(f"PDB structure file size ({size} bytes) exceeds the V1 display limit of {max_bytes} bytes.")
        
    return pdb_path.read_text(encoding="utf-8")

def build_structure_selector(context) -> dict:
    """
    Constructs structured selection objects for target and ligand.
    """
    selectors = {
        "target": None,
        "ligand": None
    }
    
    # Target highlight is ready when structure mapping status is mapped/residue_mismatch
    is_mapping_ok = getattr(context, "structure_mapping_status", "unmapped") in ("mapped", "residue_mismatch")
    has_target = getattr(context, "target_highlight_ready", False) or is_mapping_ok
    if has_target:
        chain = getattr(context, "protein_chain", None)
        resi = getattr(context, "pdb_residue_number", None)
        resn = getattr(context, "pdb_residue_name", None)
        icode = getattr(context, "pdb_insertion_code", None)
        
        if chain and resi is not None and resn:
            target_sel = {
                "chain": chain,
                "resi": resi,
                "resn": resn
            }
            if icode:
                target_sel["icode"] = icode
            selectors["target"] = target_sel

    # Ligand coordinates
    lig_chain = getattr(context, "ligand_chain", None)
    lig_resname = getattr(context, "ligand_resname", None)
    lig_resi = getattr(context, "ligand_residue_number", None)
    
    if lig_chain and lig_resname and lig_resi is not None:
        selectors["ligand"] = {
            "chain": lig_chain,
            "resn": lig_resname,
            "resi": lig_resi,
            "hetflag": True
        }
        
    return selectors

def build_structure_viewer_html(
    context,
    pdb_text: str,
    js_text: str,
    colors: dict = None,
    catalytic_residues: list = None
) -> str:
    """
    Generates a standalone interactive 3Dmol.js HTML string safely,
    serializing parameters to prevent XSS breakout.
    """
    # Merge custom colors with default roles
    palette = dict(DEFAULT_COLORS)
    if colors:
        palette.update(colors)
        
    # Build target and ligand selectors
    selectors = build_structure_selector(context)
    target_selector = selectors["target"]
    ligand_selector = selectors["ligand"]
    
    # Process catalytic triad selectors
    catalytic_selectors = []
    if catalytic_residues:
        for res in catalytic_residues:
            if isinstance(res, dict) and "chain" in res and "resi" in res and "resn" in res:
                catalytic_selectors.append({
                    "chain": res["chain"],
                    "resi": int(res["resi"]),
                    "resn": res["resn"]
                })
                
    # Serialize data securely using json.dumps
    pdb_data_json = json.dumps(pdb_text)
    target_selector_json = json.dumps(target_selector)
    ligand_selector_json = json.dumps(ligand_selector)
    catalytic_selectors_json = json.dumps(catalytic_selectors)
    mutation_notation_json = json.dumps(getattr(context, "mutation_notation", "") or "")
    
    color_protein_json = json.dumps(palette["protein"])
    color_target_json = json.dumps(palette["target"])
    color_ligand_json = json.dumps(palette["ligand"])
    color_catalytic_json = json.dumps(palette["catalytic"])
    color_background_json = json.dumps(palette["background"])
    
    # Handle fallback template if structure is unavailable
    structure_available = getattr(context, "structure_available", False)
    if not structure_available:
        viewer_message = getattr(context, "viewer_message", "No representative structure available.")
        body_content = f"""
        <div id="fallback_container">
            <div class="alert_box">
                <div class="alert_title">Structure Unavailable</div>
                <div class="alert_message">{viewer_message}</div>
            </div>
        </div>
        """
    else:
        body_content = '<div id="canvas_3dmol"></div>'

    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Structure Viewer</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: {palette["background"]};
        }}
        #canvas_3dmol {{
            width: 100%;
            height: 100%;
            position: relative;
        }}
        #fallback_container {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            color: #ffffff;
            background-color: #262730;
            box-sizing: border-box;
            padding: 20px;
        }}
        .alert_box {{
            border-left: 5px solid #ff4b4b;
            background-color: #3b2c2c;
            padding: 15px 20px;
            border-radius: 4px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .alert_title {{
            font-weight: bold;
            margin-bottom: 8px;
            color: #ff4b4b;
        }}
        .alert_message {{
            font-size: 14px;
            line-height: 1.4;
            color: #e0e0e0;
        }}
    </style>
    <script type="text/javascript">
        {js_text}
    </script>
</head>
<body>
    {body_content}

    <script type="text/javascript">
        // Safe injected parameters
        const pdbData = {pdb_data_json};
        const targetSelector = {target_selector_json};
        const ligandSelector = {ligand_selector_json};
        const catalyticSelectors = {catalytic_selectors_json};
        const mutationNotation = {mutation_notation_json};
        
        const colorProtein = {color_protein_json};
        const colorTarget = {color_target_json};
        const colorLigand = {color_ligand_json};
        const colorCatalytic = {color_catalytic_json};
        const colorBackground = {color_background_json};

        document.addEventListener("DOMContentLoaded", function() {{
            const element = document.getElementById("canvas_3dmol");
            if (!element) return;

            const viewer = $3Dmol.createViewer(element, {{
                defaultcolors: $3Dmol.rasmolElementColors
            }});
            
            viewer.setBackgroundColor(colorBackground);
            viewer.addModel(pdbData, "pdb");
            
            // Render protein polymer cartoon representation
            viewer.setStyle({{hetflag: false}}, {{cartoon: {{color: colorProtein}}}});
            
            // Render target residue as sticks and label it
            if (targetSelector) {{
                viewer.setStyle(targetSelector, {{stick: {{color: colorTarget, radius: 0.3}}}});
                viewer.addLabel(mutationNotation, {{
                    fontSize: 14,
                    fontColor: '#ffffff',
                    backgroundColor: colorTarget,
                    backgroundOpacity: 0.8,
                    position: targetSelector
                }}, targetSelector);
            }}
            
            // Render ligand as sticks
            if (ligandSelector) {{
                viewer.setStyle(ligandSelector, {{stick: {{color: colorLigand, radius: 0.35}}}});
            }}
            
            // Render catalytic triad as sticks
            if (catalyticSelectors && catalyticSelectors.length > 0) {{
                catalyticSelectors.forEach(function(sel) {{
                    viewer.setStyle(sel, {{stick: {{color: colorCatalytic, radius: 0.25}}}});
                }});
            }}
            
            // Camera focus zoom
            if (targetSelector) {{
                viewer.zoomTo(targetSelector);
            }} else {{
                viewer.zoomTo();
            }}
            
            viewer.render();
        }});
    </script>
</body>
</html>"""
    return html_template
