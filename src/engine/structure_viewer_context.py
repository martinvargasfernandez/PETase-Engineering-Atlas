class StructureViewerContext:
    """
    Immutable value object representing the aggregated 3D Structure Viewer state
    and highlight context for the user interface.
    """
    def __init__(
        self,
        atlas_position: int = None,
        atlas_reference_residue: str = None,
        atlas_mutation_label: str = None,
        study_position: int = None,
        study_current_residue: str = None,
        project_mutation_label: str = None,
        mutation_actionability: str = None,
        proposed_residue: str = None,
        mutation_notation: str = None,
        
        structure_relative_path: str = None,
        structure_type: str = None,
        protein_chain: str = None,
        
        pdb_residue_number: int = None,
        pdb_insertion_code: str = None,
        pdb_residue_name: str = None,
        
        ligand_resname: str = None,
        ligand_chain: str = None,
        ligand_residue_number: int = None,
        
        structure_mapping_status: str = "unmapped",
        structure_available: bool = False,
        target_highlight_ready: bool = False,
        viewer_ready: bool = False,
        viewer_message: str = ""
    ):
        self._atlas_position = int(atlas_position) if atlas_position is not None else None
        self._atlas_reference_residue = str(atlas_reference_residue).upper() if atlas_reference_residue is not None else None
        self._atlas_mutation_label = str(atlas_mutation_label) if atlas_mutation_label is not None else None
        self._study_position = int(study_position) if study_position is not None else None
        self._study_current_residue = str(study_current_residue).upper() if study_current_residue is not None else None
        self._project_mutation_label = str(project_mutation_label) if project_mutation_label else None
        self._mutation_actionability = str(mutation_actionability) if mutation_actionability else None
        
        self._proposed_residue = str(proposed_residue).upper() if proposed_residue is not None else None
        if self._proposed_residue is not None:
            if len(self._proposed_residue) != 1 or self._proposed_residue not in "ACDEFGHIKLMNPQRSTVWY":
                raise ValueError(f"Invalid proposed residue: {proposed_residue}")
                
        self._mutation_notation = str(mutation_notation) if mutation_notation else None
        
        # Verify consistency of mutation_notation with component fields if present
        if self._study_current_residue and self._study_position is not None and self._proposed_residue:
            expected = f"{self._study_current_residue}{self._study_position}{self._proposed_residue}"
            if self._mutation_notation is None:
                self._mutation_notation = expected
            elif self._mutation_notation != expected:
                raise ValueError(f"Inconsistent mutation notation: '{mutation_notation}', expected '{expected}'")
        
        self._structure_relative_path = str(structure_relative_path) if structure_relative_path else None
        self._structure_type = str(structure_type) if structure_type else None
        self._protein_chain = str(protein_chain) if protein_chain else None
        
        self._pdb_residue_number = int(pdb_residue_number) if pdb_residue_number is not None else None
        self._pdb_insertion_code = str(pdb_insertion_code).strip() if pdb_insertion_code is not None else None
        if self._pdb_insertion_code == "None" or not self._pdb_insertion_code:
            self._pdb_insertion_code = None
            
        self._pdb_residue_name = str(pdb_residue_name).upper() if pdb_residue_name is not None else None
        
        self._ligand_resname = str(ligand_resname).upper() if ligand_resname else None
        self._ligand_chain = str(ligand_chain) if ligand_chain else None
        self._ligand_residue_number = int(ligand_residue_number) if ligand_residue_number is not None else None
        
        self._structure_mapping_status = str(structure_mapping_status)
        self._structure_available = bool(structure_available)
        
        # viewer_ready requires structure_available
        self._viewer_ready = bool(viewer_ready) if self._structure_available else False
        
        # target_highlight_ready requires viewer_ready and mapped or residue_mismatch status
        is_mapping_ok = self._structure_mapping_status in ("mapped", "residue_mismatch")
        self._target_highlight_ready = bool(target_highlight_ready) if (self._viewer_ready and is_mapping_ok) else False
        
        self._viewer_message = str(viewer_message)

    @property
    def atlas_position(self) -> int:
        return self._atlas_position

    @property
    def atlas_reference_residue(self) -> str:
        return self._atlas_reference_residue

    @property
    def atlas_mutation_label(self) -> str:
        return self._atlas_mutation_label

    @property
    def study_position(self) -> int:
        return self._study_position

    @property
    def study_current_residue(self) -> str:
        return self._study_current_residue

    @property
    def project_mutation_label(self) -> str:
        return self._project_mutation_label

    @property
    def mutation_actionability(self) -> str:
        return self._mutation_actionability

    @property
    def proposed_residue(self) -> str:
        return self._proposed_residue

    @property
    def mutation_notation(self) -> str:
        return self._mutation_notation

    @property
    def structure_relative_path(self) -> str:
        return self._structure_relative_path

    @property
    def structure_type(self) -> str:
        return self._structure_type

    @property
    def protein_chain(self) -> str:
        return self._protein_chain

    @property
    def pdb_residue_number(self) -> int:
        return self._pdb_residue_number

    @property
    def pdb_insertion_code(self) -> str:
        return self._pdb_insertion_code

    @property
    def pdb_residue_name(self) -> str:
        return self._pdb_residue_name

    @property
    def ligand_resname(self) -> str:
        return self._ligand_resname

    @property
    def ligand_chain(self) -> str:
        return self._ligand_chain

    @property
    def ligand_residue_number(self) -> int:
        return self._ligand_residue_number

    @property
    def structure_mapping_status(self) -> str:
        return self._structure_mapping_status

    @property
    def structure_available(self) -> bool:
        return self._structure_available

    @property
    def target_highlight_ready(self) -> bool:
        return self._target_highlight_ready

    @property
    def viewer_ready(self) -> bool:
        return self._viewer_ready

    @property
    def viewer_message(self) -> str:
        return self._viewer_message

    def to_dict(self) -> dict:
        return {
            "atlas_position": self.atlas_position,
            "atlas_reference_residue": self.atlas_reference_residue,
            "atlas_mutation_label": self.atlas_mutation_label,
            "study_position": self.study_position,
            "study_current_residue": self.study_current_residue,
            "project_mutation_label": self.project_mutation_label,
            "mutation_actionability": self.mutation_actionability,
            "proposed_residue": self.proposed_residue,
            "mutation_notation": self.mutation_notation,
            "structure_relative_path": self.structure_relative_path,
            "structure_type": self.structure_type,
            "protein_chain": self.protein_chain,
            "pdb_residue_number": self.pdb_residue_number,
            "pdb_insertion_code": self.pdb_insertion_code,
            "pdb_residue_name": self.pdb_residue_name,
            "ligand_resname": self.ligand_resname,
            "ligand_chain": self.ligand_chain,
            "ligand_residue_number": self.ligand_residue_number,
            "structure_mapping_status": self.structure_mapping_status,
            "structure_available": self.structure_available,
            "target_highlight_ready": self.target_highlight_ready,
            "viewer_ready": self.viewer_ready,
            "viewer_message": self.viewer_message
        }
