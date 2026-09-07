class StructuralResidueMapping:
    """
    Immutable value object representing the mapping of one StudySequence residue 
    position to a corresponding PDB structure residue record.
    """
    VALID_STATUSES = {
        "mapped",
        "unmapped",
        "residue_mismatch",
        "missing_pdb_residue",
        "chain_missing",
        "invalid_structure",
        "invalid_study_position"
    }

    def __init__(
        self,
        study_position: int,
        study_residue: str = None,
        pdb_chain: str = None,
        pdb_residue_number: int = None,
        pdb_insertion_code: str = None,
        pdb_residue_name: str = None,
        pdb_residue_one_letter: str = None,
        mapping_status: str = "unmapped",
        mapping_method: str = "pairwise_alignment",
        message: str = ""
    ):
        if mapping_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid mapping_status: {mapping_status}. Must be one of {self.VALID_STATUSES}")

        # Normalizations
        norm_insertion_code = None
        if pdb_insertion_code is not None:
            norm_val = str(pdb_insertion_code).strip()
            if norm_val and norm_val != "None":
                norm_insertion_code = norm_val

        # Validate invariants
        if mapping_status in ("mapped", "residue_mismatch"):
            if study_position is None or study_position <= 0:
                raise ValueError(f"study_position must be a positive 1-based integer for status '{mapping_status}'.")
            if not pdb_chain:
                raise ValueError(f"pdb_chain is mandatory for status '{mapping_status}'.")
            if pdb_residue_number is None:
                raise ValueError(f"pdb_residue_number is mandatory for status '{mapping_status}'.")
            if not pdb_residue_name:
                raise ValueError(f"pdb_residue_name is mandatory for status '{mapping_status}'.")
            if not pdb_residue_one_letter:
                raise ValueError(f"pdb_residue_one_letter is mandatory for status '{mapping_status}'.")
            if not study_residue:
                raise ValueError(f"study_residue is mandatory for status '{mapping_status}'.")
        else:
            # Failure states must not fabricate coordinate information
            pdb_chain = None
            pdb_residue_number = None
            norm_insertion_code = None
            pdb_residue_name = None
            pdb_residue_one_letter = None

        # Immutability backing fields
        self._study_position = int(study_position) if study_position is not None else None
        self._study_residue = str(study_residue).upper() if study_residue is not None else None
        self._pdb_chain = str(pdb_chain) if pdb_chain is not None else None
        self._pdb_residue_number = int(pdb_residue_number) if pdb_residue_number is not None else None
        self._pdb_insertion_code = norm_insertion_code
        self._pdb_residue_name = str(pdb_residue_name).upper() if pdb_residue_name is not None else None
        self._pdb_residue_one_letter = str(pdb_residue_one_letter).upper() if pdb_residue_one_letter is not None else None
        self._mapping_status = str(mapping_status)
        self._mapping_method = str(mapping_method)
        self._message = str(message)

    @property
    def study_position(self) -> int:
        return self._study_position

    @property
    def study_residue(self) -> str:
        return self._study_residue

    @property
    def pdb_chain(self) -> str:
        return self._pdb_chain

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
    def pdb_residue_one_letter(self) -> str:
        return self._pdb_residue_one_letter

    @property
    def mapping_status(self) -> str:
        return self._mapping_status

    @property
    def mapping_method(self) -> str:
        return self._mapping_method

    @property
    def message(self) -> str:
        return self._message

    @property
    def is_mapped(self) -> bool:
        return self.mapping_status in ("mapped", "residue_mismatch")

    @property
    def can_highlight(self) -> bool:
        return self.mapping_status in ("mapped", "residue_mismatch")

    def to_dict(self) -> dict:
        return {
            "study_position": self.study_position,
            "study_residue": self.study_residue,
            "pdb_chain": self.pdb_chain,
            "pdb_residue_number": self.pdb_residue_number,
            "pdb_insertion_code": self.pdb_insertion_code,
            "pdb_residue_name": self.pdb_residue_name,
            "pdb_residue_one_letter": self.pdb_residue_one_letter,
            "mapping_status": self.mapping_status,
            "mapping_method": self.mapping_method,
            "message": self.message,
            "is_mapped": self.is_mapped,
            "can_highlight": self.can_highlight
        }
