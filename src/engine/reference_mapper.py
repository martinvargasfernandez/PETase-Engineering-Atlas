import hashlib
import Bio
from Bio.Align import PairwiseAligner, substitution_matrices
from engine.atlas import load_master_table
from engine.mapping_status import MappingStatus
from engine.mapped_residue import MappedResidue
from engine.mapping_result import MappingResult

class StructureAvailabilityResult:
    """
    Immutable value object representing the parsed structure state.
    """
    def __init__(
        self,
        structure_available: bool,
        viewer_ready: bool,
        status: str,
        message: str
    ):
        self._structure_available = bool(structure_available)
        self._viewer_ready = bool(viewer_ready)
        self._status = str(status)
        self._message = str(message)

    @property
    def structure_available(self) -> bool:
        return self._structure_available

    @property
    def viewer_ready(self) -> bool:
        return self._viewer_ready

    @property
    def status(self) -> str:
        return self._status

    @property
    def message(self) -> str:
        return self._message

class ReferenceMapper:
    """
    Scientific Execution Engine: ReferenceMapper

    Responsible for:
    - reconstructing target coordinate reference templates
    - aligning query sequences utilizing global Dynamic Programming (Biopython backend)
    - outputting immutable MappingResult instances

    It does NOT perform HMM searches, METAGENOME family classifications,
    docking calculations, or conservation updates.
    """

    def __init__(self, coordinate_system: str = "IsPETase_v1"):
        if coordinate_system != "IsPETase_v1":
            raise ValueError(f"Unsupported coordinate system '{coordinate_system}'.")
        self._coordinate_system = coordinate_system
        self._reference_name = "IsPETase_v1_reference"
        self._cached_structure_path = None
        self._cached_structure = None

    def check_structure_availability(
        self,
        structure_path: str,
        protein_chain: str
    ) -> StructureAvailabilityResult:
        """
        Validates whether a structure file exists and can be parsed, and checks
        for protein chain presence. Rejects CIF/mmCIF formats deterministically in V1.
        """
        from pathlib import Path
        if not structure_path:
            return StructureAvailabilityResult(
                structure_available=False,
                viewer_ready=False,
                status="invalid_structure",
                message="Structure file path is empty."
            )

        p = Path(structure_path)
        if p.suffix.lower() in (".cif", ".mmcif"):
            return StructureAvailabilityResult(
                structure_available=False,
                viewer_ready=False,
                status="invalid_structure",
                message="mmCIF is not supported in Structure Mapping V1"
            )

        if not p.exists() or not p.is_file():
            return StructureAvailabilityResult(
                structure_available=False,
                viewer_ready=False,
                status="invalid_structure",
                message=f"Structure file not found: {structure_path}"
            )

        from Bio.PDB import PDBParser
        import logging
        logging.getLogger("Biopython").setLevel(logging.ERROR)

        resolved_path = str(p.resolve())
        if self._cached_structure_path == resolved_path and self._cached_structure is not None:
            structure = self._cached_structure
        else:
            try:
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("struct", resolved_path)
                self._cached_structure_path = resolved_path
                self._cached_structure = structure
            except Exception as e:
                return StructureAvailabilityResult(
                    structure_available=False,
                    viewer_ready=False,
                    status="invalid_structure",
                    message=f"Failed to parse PDB structure: {str(e)}"
                )

        try:
            model = structure[0]
        except KeyError:
            return StructureAvailabilityResult(
                structure_available=True,
                viewer_ready=False,
                status="invalid_structure",
                message="PDB structure contains no models (malformed)."
            )

        if not protein_chain or protein_chain not in model:
            return StructureAvailabilityResult(
                structure_available=True,
                viewer_ready=False,
                status="chain_missing",
                message=f"Target protein chain '{protein_chain}' is missing from PDB model."
            )

        return StructureAvailabilityResult(
            structure_available=True,
            viewer_ready=True,
            status="mapped",
            message="Structure ready for 3D display."
        )

    @property
    def coordinate_system(self) -> str:
        return self._coordinate_system

    def get_reference_sequence(self) -> str:
        """
        Loads and reconstructs the reference sequence from the master position table.
        """
        df = load_master_table()
        df_sorted = df.sort_values("IsPETase_position")
        return "".join(df_sorted["IsPETase_residue"].tolist())

    def map_sequence(self, study_sequence) -> MappingResult:
        # Duck typing verification for StudySequence
        if not hasattr(study_sequence, "study_id") or not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")

        ref_seq = self.get_reference_sequence()
        ref_len = len(ref_seq)
        
        # Calculate reference sequence hash
        sha = hashlib.sha256()
        sha.update(ref_seq.encode("utf-8"))
        ref_hash = sha.hexdigest()

        # Handle incompatible accepted residues (J, U, O) for BLOSUM62 matrix
        matrix = substitution_matrices.load("BLOSUM62")
        blosum_alphabet = frozenset(matrix.alphabet)
        
        temp_query_chars = []
        compatibility_warnings = []
        
        # Original letters for later recovery
        orig_seq = study_sequence.normalized_sequence
        
        for idx, char in enumerate(orig_seq):
            if char not in blosum_alphabet:
                # Replace with X only in the temporary alignment input
                temp_query_chars.append("X")
                # Warning positions use 1-based study coordinates (idx + 1)
                compatibility_warnings.append(
                    f"Character '{char}' at study position {idx + 1} was temporarily replaced with 'X' for alignment compatibility."
                )
            else:
                temp_query_chars.append(char)
        
        temp_query_seq = "".join(temp_query_chars)

        # Configure Bio.Align.PairwiseAligner
        aligner = PairwiseAligner()
        aligner.mode = "global"
        aligner.substitution_matrix = matrix
        
        # Explicitly set gap penalties to enforce strict global behaviour
        aligner.open_gap_score = -10.0
        aligner.extend_gap_score = -0.5
        aligner.open_end_gap_score = -10.0
        aligner.extend_end_gap_score = -0.5

        # Execute alignment
        alignments = aligner.align(ref_seq, temp_query_seq)
        
        # Handle multiple optimal alignments (safe capped check)
        try:
            raw_count = len(alignments)
            if hasattr(raw_count, "item"):
                raw_count = raw_count.item()
            opt_count = int(raw_count)
        except OverflowError:
            # Handle OverflowError safely when alignments list is huge
            opt_count = None
        except Exception:
            opt_count = 1
            
        is_ambiguous = (opt_count is None) or (opt_count > 1)
        
        warnings_list = list(study_sequence.validation_warnings) + compatibility_warnings
        if is_ambiguous:
            warnings_list.append({
                "code": "MULTIPLE_OPTIMAL_ALIGNMENTS",
                "message": "More than one optimal alignment was detected; the first deterministic alignment was used."
            })

        # Get first optimal alignment deterministically
        alignment = alignments[0]
        score = alignment.score

        # Extract backtrack path indices
        indices = alignment.indices
        alignment_len = int(len(indices[0]))

        mapped_residues = []
        exact_matches = 0
        substitutions = 0
        insertions = 0
        deletions = 0
        unmapped_residues = 0

        from engine.atlas_position import AtlasPosition

        for col_idx in range(alignment_len):
            # Convert numpy int64 values to native Python ints
            t_idx = int(indices[0][col_idx].item())
            q_idx = int(indices[1][col_idx].item())

            if t_idx != -1 and q_idx != -1:
                # Residue-aligned coordinate
                study_pos = q_idx + 1
                # Preserve the original StudySequence character instead of the temporary replacement 'X'
                orig_char = orig_seq[q_idx]
                
                atlas_pos = AtlasPosition(t_idx + 1)
                ref_char = ref_seq[t_idx]

                if orig_char == ref_char:
                    status = MappingStatus.EXACT_MATCH
                    exact_matches += 1
                else:
                    status = MappingStatus.SUBSTITUTION
                    substitutions += 1

                mr = MappedResidue(
                    study_sequence=study_sequence,
                    mapping_status=status,
                    study_position=study_pos,
                    study_residue=orig_char,
                    atlas_position=atlas_pos,
                    mapping_confidence=None # Always None in version 1
                )
                mapped_residues.append(mr)

            elif t_idx == -1 and q_idx != -1:
                # Insertion in query sequence (gap in reference)
                study_pos = q_idx + 1
                orig_char = orig_seq[q_idx]
                
                status = MappingStatus.INSERTION
                insertions += 1

                mr = MappedResidue(
                    study_sequence=study_sequence,
                    mapping_status=status,
                    study_position=study_pos,
                    study_residue=orig_char,
                    atlas_position=None,
                    mapping_confidence=None
                )
                mapped_residues.append(mr)

            elif t_idx != -1 and q_idx == -1:
                # Deletion in query sequence (gap in study sequence)
                atlas_pos = AtlasPosition(t_idx + 1)
                
                status = MappingStatus.DELETION
                deletions += 1

                mr = MappedResidue(
                    study_sequence=study_sequence,
                    mapping_status=status,
                    study_position=None,
                    study_residue=None,
                    atlas_position=atlas_pos,
                    mapping_confidence=None
                )
                mapped_residues.append(mr)

        # Construct scoring parameters provenance dictionary
        scoring_params = {
            "substitution_matrix": "BLOSUM62",
            "open_gap_score": aligner.open_gap_score,
            "extend_gap_score": aligner.extend_gap_score,
            "open_end_gap_score": aligner.open_end_gap_score,
            "extend_end_gap_score": aligner.extend_end_gap_score,
        }

        return MappingResult(
            study_sequence=study_sequence,
            mapped_residues=mapped_residues,
            alignment_score=score,
            exact_matches=exact_matches,
            substitutions=substitutions,
            insertions=insertions,
            deletions=deletions,
            unmapped_residues=unmapped_residues,
            study_length=study_sequence.length,
            reference_length=ref_len,
            alignment_length=alignment_len,
            alignment_method="pairwise_global",
            scoring_parameters=scoring_params,
            reference_sequence_hash=ref_hash,
            coordinate_system=self.coordinate_system,
            reference_name=self._reference_name,
            biopython_version=Bio.__version__,
            optimal_alignment_count=opt_count,
            alignment_is_ambiguous=is_ambiguous,
            warnings=warnings_list
        )

    def map_study_to_structure(
        self,
        study_sequence,
        structure_path: str,
        protein_chain: str,
        study_position: int
    ) -> "StructuralResidueMapping":
        """
        Extracts sequence from PDB chain, aligns it to study sequence, and resolves
        the mapping details of a target study position.
        """
        from pathlib import Path
        from engine.structural_residue_mapping import StructuralResidueMapping
        
        # 1. Validate study position
        if not hasattr(study_sequence, "normalized_sequence"):
            raise TypeError("study_sequence must implement the StudySequence interface.")
        
        study_seq_str = study_sequence.normalized_sequence
        if study_position is None or study_position <= 0 or study_position > len(study_seq_str):
            return StructuralResidueMapping(
                study_position=study_position,
                mapping_status="invalid_study_position",
                message=f"Study position {study_position} is out of bounds (1 to {len(study_seq_str)})."
            )
            
        study_residue = study_seq_str[study_position - 1]

        # 2. Parse PDB structure
        if not structure_path:
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="invalid_structure",
                message="Structure file path is empty."
            )
            
        p = Path(structure_path)
        if p.suffix.lower() in (".cif", ".mmcif"):
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="invalid_structure",
                message="mmCIF is not supported in Structure Mapping V1"
            )

        if not p.exists() or not p.is_file():
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="invalid_structure",
                message=f"Structure file not found: {structure_path}"
            )
            
        from Bio.PDB import PDBParser
        import logging
        
        # Disable Bio.PDB warnings to keep stdout clean
        logging.getLogger("Biopython").setLevel(logging.ERROR)
        
        resolved_path = str(p.resolve())
        if self._cached_structure_path == resolved_path and self._cached_structure is not None:
            structure = self._cached_structure
        else:
            try:
                parser = PDBParser(QUIET=True)
                structure = parser.get_structure("struct", resolved_path)
                self._cached_structure_path = resolved_path
                self._cached_structure = structure
            except Exception as e:
                return StructuralResidueMapping(
                    study_position=study_position,
                    study_residue=study_residue,
                    mapping_status="invalid_structure",
                    message=f"Failed to parse PDB structure: {str(e)}"
                )

        # 3. Retrieve chain
        try:
            model = structure[0]
        except KeyError:
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="invalid_structure",
                message="Structure has no model records (empty or malformed file)."
            )
        if protein_chain not in model:
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="chain_missing",
                message=f"Chain '{protein_chain}' not found in the structure."
            )
            
        chain = model[protein_chain]

        # Standard three-to-one letter conversion map
        THREE_TO_ONE = {
            "ALA": "A", "CYS": "C", "ASP": "D", "GLU": "E", "PHE": "F",
            "GLY": "G", "HIS": "H", "ILE": "I", "LYS": "K", "LEU": "L",
            "MET": "M", "ASN": "N", "PRO": "P", "GLN": "Q", "ARG": "R",
            "SER": "S", "THR": "T", "VAL": "V", "TRP": "W", "TYR": "Y",
            "MSE": "M"  # MSE normalized to M
        }

        pdb_seq_chars = []
        pdb_residues_metadata = [] # List of dicts

        for residue in chain:
            res_id = residue.id
            het_flag = res_id[0]
            resname = residue.resname.strip().upper()
            
            # Allow standard residues and MSE
            is_standard = (het_flag == ' ' or het_flag.strip() == '')
            is_mse = (het_flag == 'H_MSE' or resname == 'MSE')
            
            if not (is_standard or is_mse):
                continue
                
            one_letter = THREE_TO_ONE.get(resname, "X")
            
            pdb_seq_chars.append(one_letter)
            pdb_residues_metadata.append({
                "resname": resname,
                "one_letter": one_letter,
                "number": res_id[1],
                "icode": res_id[2]
            })
            
        pdb_seq_str = "".join(pdb_seq_chars)
        if not pdb_seq_str:
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="unmapped",
                message="No protein residues found in the specified PDB chain."
            )

        # 4. Align study sequence and PDB sequence
        from Bio.Align import PairwiseAligner, substitution_matrices
        matrix = substitution_matrices.load("BLOSUM62")
        blosum_alphabet = frozenset(matrix.alphabet)
        
        temp_query_chars = []
        for char in study_seq_str:
            if char not in blosum_alphabet:
                temp_query_chars.append("X")
            else:
                temp_query_chars.append(char)
        temp_query_seq = "".join(temp_query_chars)
        
        temp_pdb_chars = []
        for char in pdb_seq_str:
            if char not in blosum_alphabet:
                temp_pdb_chars.append("X")
            else:
                temp_pdb_chars.append(char)
        temp_pdb_seq = "".join(temp_pdb_chars)
        
        aligner = PairwiseAligner()
        aligner.mode = "global"
        aligner.substitution_matrix = matrix
        aligner.open_gap_score = -10.0
        aligner.extend_gap_score = -0.5
        aligner.open_end_gap_score = -10.0
        aligner.extend_end_gap_score = -0.5
        
        alignments = aligner.align(temp_pdb_seq, temp_query_seq)
        alignment = alignments[0]
        indices = alignment.indices
        alignment_len = int(len(indices[0]))
        
        query_target_idx = study_position - 1
        mapped_target_idx = None
        is_deletion = False
        
        for col_idx in range(alignment_len):
            t_idx = int(indices[0][col_idx].item())
            q_idx = int(indices[1][col_idx].item())
            
            if q_idx == query_target_idx:
                if t_idx == -1:
                    is_deletion = True
                else:
                    mapped_target_idx = t_idx
                break
                
        if is_deletion:
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="missing_pdb_residue",
                message="Study position aligns to a gap (deletion) in the PDB structure."
            )
            
        if mapped_target_idx is None:
            return StructuralResidueMapping(
                study_position=study_position,
                study_residue=study_residue,
                mapping_status="unmapped",
                message="Study position could not be mapped to the PDB structure."
            )
            
        res_meta = pdb_residues_metadata[mapped_target_idx]
        pdb_res_one_letter = res_meta["one_letter"]
        pdb_res_name = res_meta["resname"]
        pdb_res_number = res_meta["number"]
        pdb_res_icode = res_meta["icode"]
        
        if study_residue == pdb_res_one_letter:
            status = "mapped"
            msg = f"Study residue {study_residue}{study_position} successfully mapped to PDB residue {pdb_res_name} {pdb_res_number}."
        else:
            status = "residue_mismatch"
            msg = f"Study residue {study_residue}{study_position} aligns to PDB residue {pdb_res_name} {pdb_res_number} (identity mismatch)."
            
        return StructuralResidueMapping(
            study_position=study_position,
            study_residue=study_residue,
            pdb_chain=protein_chain,
            pdb_residue_number=pdb_res_number,
            pdb_insertion_code=pdb_res_icode,
            pdb_residue_name=pdb_res_name,
            pdb_residue_one_letter=pdb_res_one_letter,
            mapping_status=status,
            mapping_method="pairwise_alignment",
            message=msg
        )
