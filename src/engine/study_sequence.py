import hashlib
import json
import uuid

class StudySequence:
    """
    Scientific Entity

    StudySequence

    Represents one researcher-supplied protein sequence.

    Responsible only for:
    - sequence normalization
    - validation
    - metadata
    - serialization

    It does NOT perform:
    - alignment
    - reference mapping
    - family classification
    - project persistence
    - docking
    - molecular dynamics
    - Atlas queries
    
    Attributes:
        length: represents the submitted normalized amino-acid sequence.
                It is NOT: mapped length, mature protein length, or Atlas coordinate count.
    """

    @classmethod
    def from_fasta(
        cls,
        fasta_string: str,
        study_id: str = None
    ) -> "StudySequence":
        """
        Parses a single-record FASTA formatted string or a sequence-only string,
        normalizes/validates it, and returns a StudySequence instance.
        """
        if fasta_string is None:
            raise ValueError("fasta_string cannot be None.")

        # Split into lines and strip trailing/leading whitespace, removing empty lines
        lines = [line.strip() for line in fasta_string.splitlines()]
        lines = [line for line in lines if line]

        if not lines:
            raise ValueError("FASTA input is empty.")

        header = None
        seq_parts = []

        # Check if first line is a header
        first_line = lines[0]
        if first_line.startswith(">"):
            header = first_line
            # Count how many lines start with >
            headers_count = sum(1 for line in lines if line.startswith(">"))
            if headers_count > 1:
                raise ValueError("FASTA input contains more than one record.")
            # Gather sequence lines
            for line in lines[1:]:
                seq_parts.append(line)
            if not seq_parts:
                raise ValueError("FASTA header present but sequence is empty.")
        else:
            # Check if there are any headers in subsequent lines
            headers_count = sum(1 for line in lines if line.startswith(">"))
            if headers_count > 0:
                raise ValueError("FASTA header found after sequence lines or multiple records present.")
            # Sequence only input
            seq_parts = lines

        raw_sequence = "".join(seq_parts)
        if not raw_sequence or not raw_sequence.strip():
            raise ValueError("Sequence is empty.")

        return cls(
            raw_sequence=raw_sequence,
            fasta_header=header,
            study_id=study_id
        )

    def __init__(
        self,
        raw_sequence: str,
        fasta_header: str = None,
        name: str = None,
        description: str = None,
        source: str = None,
        metadata: dict = None,
        study_id: str = None
    ):
        if raw_sequence is None:
            raise ValueError("raw_sequence cannot be None.")

        self._raw_sequence = raw_sequence
        
        # 1. Normalize sequence content
        from engine.sequence_validation import normalize_sequence, validate_sequence
        normalized = normalize_sequence(raw_sequence)
        self._normalized_sequence = normalized
        self._length = len(normalized)
        
        # 2. Perform validations
        self._warnings = list(validate_sequence(normalized))

        # 3. Handle identifiers and metadata
        self._study_id = str(study_id) if study_id is not None else str(uuid.uuid4())
        
        # Header processing (strip leading '>')
        if fasta_header is not None:
            header_str = str(fasta_header).lstrip(">").strip()
            self._fasta_header = header_str
        else:
            self._fasta_header = None

        # Name and description fallback logic
        if name is not None:
            self._name = str(name)
        elif self._fasta_header:
            tokens = self._fasta_header.split()
            self._name = tokens[0] if tokens else "StudySequence"
        else:
            self._name = "StudySequence"

        if description is not None:
            self._description = str(description)
        elif self._fasta_header:
            tokens = self._fasta_header.split(maxsplit=1)
            self._description = tokens[1] if len(tokens) > 1 else ""
        else:
            self._description = ""

        self._source = str(source) if source is not None else None
        self._metadata = dict(metadata) if metadata is not None else {}

        # 4. Calculate deterministic sequence_hash (exclusively based on normalized sequence content)
        sha = hashlib.sha256()
        sha.update(self._normalized_sequence.encode("utf-8"))
        self._sequence_hash = sha.hexdigest()

    @property
    def study_id(self) -> str:
        return self._study_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def fasta_header(self) -> str:
        return self._fasta_header

    @property
    def raw_sequence(self) -> str:
        return self._raw_sequence

    @property
    def normalized_sequence(self) -> str:
        return self._normalized_sequence

    @property
    def length(self) -> int:
        return self._length

    @property
    def source(self) -> str:
        return self._source

    @property
    def metadata(self) -> dict:
        return dict(self._metadata)

    @property
    def is_valid(self) -> bool:
        return True

    @property
    def validation_warnings(self) -> tuple:
        return tuple(self._warnings)

    @property
    def sequence_hash(self) -> str:
        return self._sequence_hash

    def describe(self) -> str:
        """
        Returns a concise and factual textual description of the StudySequence.
        """
        header_part = f" | Header: {self.fasta_header}" if self.fasta_header else ""
        source_part = f" | Source: {self.source}" if self.source is not None else ""
        return (
            f"StudySequence ID: {self.study_id} | "
            f"Name: {self.name} | "
            f"Length: {self.length}{source_part}{header_part} | "
            f"Hash Prefix: {self.sequence_hash[:12]} | "
            f"Warnings: {len(self._warnings)}"
        )

    def to_dict(self) -> dict:
        """
        Export the StudySequence object as a dictionary of native Python values.
        """
        return {
            "entity": "StudySequence",
            "schema_version": 1,
            "study_id": self.study_id,
            "name": self.name,
            "description": self.description,
            "fasta_header": self.fasta_header,
            "raw_sequence": self.raw_sequence,
            "normalized_sequence": self.normalized_sequence,
            "length": self.length,
            "source": self.source,
            "metadata": self.metadata,
            "is_valid": self.is_valid,
            "validation_warnings": list(self.validation_warnings),
            "sequence_hash": self.sequence_hash,
        }

    def to_json(self) -> str:
        """
        Serializes the cleaned dictionary representation to a JSON string.
        """
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_fasta(self) -> str:
        """
        Returns a valid FASTA formatted string wrapped to 60 characters per line.
        """
        header = self.fasta_header if self.fasta_header is not None else self.study_id
        fasta_header_line = f">{header}\n"
        
        lines = []
        for i in range(0, len(self._normalized_sequence), 60):
            lines.append(self._normalized_sequence[i:i+60])
        
        return fasta_header_line + "\n".join(lines) + "\n"