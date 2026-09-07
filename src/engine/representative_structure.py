import re

class RepresentativeStructure:
    """
    Value Object representing a validated representative structure associated with a CaseStudy.
    This class is immutable.
    """
    VALID_STRUCTURE_TYPES = {
        "experimental",
        "predicted",
        "docking_pose",
        "md_representative",
        "other"
    }

    def __init__(
        self,
        relative_path: str,
        structure_type: str,
        protein_chain: str,
        checksum_sha256: str,
        size_bytes: int,
        ligand_resname: str = None,
        ligand_chain: str = None,
        ligand_residue_number: int = None,
        description: str = ""
    ):
        # 1. Path validations
        if not relative_path:
            raise ValueError("relative_path is mandatory.")
        
        norm_path = relative_path.replace("\\", "/")
        if not norm_path.startswith("attachments/"):
            raise ValueError("relative_path must begin with 'attachments/'.")
        if ".." in norm_path:
            raise ValueError("relative_path cannot contain directory traversal '..' components.")
        if ":" in norm_path or norm_path.startswith("/"):
            raise ValueError("relative_path cannot be an absolute or drive path.")

        # 2. Structure type validations
        if structure_type not in self.VALID_STRUCTURE_TYPES:
            raise ValueError(f"Invalid structure_type: {structure_type}. Must be one of {self.VALID_STRUCTURE_TYPES}")

        # 3. Protein chain validation
        if not protein_chain:
            raise ValueError("protein_chain is mandatory.")

        # 4. Checksum validation
        if not checksum_sha256:
            raise ValueError("checksum_sha256 is mandatory.")
        if not re.match(r"^[a-fA-F0-9]{64}$", checksum_sha256):
            raise ValueError("checksum_sha256 must be a valid 64-character SHA-256 hex string.")

        # 5. Size validation
        if not isinstance(size_bytes, int) or size_bytes < 0:
            raise ValueError("size_bytes must be a non-negative integer.")

        # 6. Ligand group validation (all absent or all present)
        ligand_fields = [ligand_resname, ligand_chain, ligand_residue_number]
        has_any_ligand = any(lf is not None for lf in ligand_fields)
        has_all_ligand = all(lf is not None for lf in ligand_fields)
        if has_any_ligand and not has_all_ligand:
            raise ValueError(
                "Ligand fields (ligand_resname, ligand_chain, ligand_residue_number) must be either all present or all absent."
            )

        if ligand_residue_number is not None:
            if not isinstance(ligand_residue_number, int):
                raise ValueError("ligand_residue_number must be an integer.")

        # Assign properties (immutability pattern)
        self._relative_path = norm_path
        self._structure_type = str(structure_type)
        self._protein_chain = str(protein_chain)
        self._checksum_sha256 = str(checksum_sha256)
        self._size_bytes = int(size_bytes)
        
        self._ligand_resname = str(ligand_resname) if ligand_resname is not None else None
        self._ligand_chain = str(ligand_chain) if ligand_chain is not None else None
        self._ligand_residue_number = ligand_residue_number
        self._description = str(description) if description is not None else ""

    @property
    def relative_path(self) -> str:
        return self._relative_path

    @property
    def structure_type(self) -> str:
        return self._structure_type

    @property
    def protein_chain(self) -> str:
        return self._protein_chain

    @property
    def checksum_sha256(self) -> str:
        return self._checksum_sha256

    @property
    def size_bytes(self) -> int:
        return self._size_bytes

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
    def description(self) -> str:
        return self._description

    def to_dict(self) -> dict:
        d = {
            "relative_path": self.relative_path,
            "structure_type": self.structure_type,
            "protein_chain": self.protein_chain,
            "checksum_sha256": self.checksum_sha256,
            "size_bytes": self.size_bytes,
            "description": self.description
        }
        if self.ligand_resname is not None:
            d["ligand_resname"] = self.ligand_resname
            d["ligand_chain"] = self.ligand_chain
            d["ligand_residue_number"] = self.ligand_residue_number
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "RepresentativeStructure":
        if not data:
            return None
        return cls(
            relative_path=data.get("relative_path"),
            structure_type=data.get("structure_type"),
            protein_chain=data.get("protein_chain"),
            checksum_sha256=data.get("checksum_sha256"),
            size_bytes=data.get("size_bytes"),
            ligand_resname=data.get("ligand_resname"),
            ligand_chain=data.get("ligand_chain"),
            ligand_residue_number=data.get("ligand_residue_number"),
            description=data.get("description", "")
        )
