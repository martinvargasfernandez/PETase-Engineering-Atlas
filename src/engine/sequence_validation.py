STANDARD_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")
AMBIGUOUS_AMINO_ACIDS = frozenset("XBZJ")
NON_STANDARD_AMINO_ACIDS = frozenset("UO")
ACCEPTED_AMINO_ACIDS = STANDARD_AMINO_ACIDS | AMBIGUOUS_AMINO_ACIDS | NON_STANDARD_AMINO_ACIDS

def normalize_sequence(raw_sequence: str) -> str:
    """
    Strips all whitespaces and line breaks, and converts to uppercase.
    """
    if raw_sequence is None:
        raise ValueError("raw_sequence cannot be None.")
    return "".join(raw_sequence.split()).upper()

def validate_sequence(normalized_sequence: str) -> tuple[str, ...]:
    """
    Validates a normalized sequence, accumulating non-fatal warnings and
    raising ValueError on fatal characters or empty sequences.
    """
    if not normalized_sequence:
        raise ValueError("StudySequence cannot be empty.")
    
    warnings = []
    for idx, char in enumerate(normalized_sequence):
        if char in STANDARD_AMINO_ACIDS:
            continue
        elif char in AMBIGUOUS_AMINO_ACIDS:
            warnings.append(f"Ambiguous residue '{char}' at index {idx}.")
        elif char in NON_STANDARD_AMINO_ACIDS:
            warnings.append(f"Non-standard residue '{char}' at index {idx}.")
        else:
            raise ValueError(f"Invalid character '{char}' at index {idx} in raw sequence.")
    return tuple(warnings)

def validate_amino_acid(amino_acid: str) -> tuple[str, tuple[str, ...]]:
    """
    Validates exactly one non-whitespace character.
    Returns normalized uppercase character and a tuple of non-fatal warnings.
    Raises ValueError for unsupported characters or wrong input length.
    """
    if amino_acid is None:
        raise ValueError("Amino acid cannot be None.")
    
    stripped = amino_acid.strip()
    if len(stripped) != 1:
        raise ValueError("Amino acid must be exactly one character.")
        
    char = stripped.upper()
    if char not in ACCEPTED_AMINO_ACIDS:
        raise ValueError(f"Invalid character '{amino_acid}' in raw sequence.")
        
    warnings = []
    if char in AMBIGUOUS_AMINO_ACIDS:
        warnings.append(f"Ambiguous residue '{char}'.")
    elif char in NON_STANDARD_AMINO_ACIDS:
        warnings.append(f"Non-standard residue '{char}'.")
        
    return char, tuple(warnings)
