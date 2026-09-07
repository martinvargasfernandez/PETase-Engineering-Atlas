class CaseStudy:
    """
    Scientific object representing enzyme-specific evidence.

    CaseStudy evidence includes docking, molecular dynamics,
    residue-PET contacts, residue-PET interaction energies,
    hydrogen bonds and structural observations.

    This evidence must not modify the global Atlas Evidence Score.
    """

    def __init__(self, name: str, enzyme_name: str):
        self.name = name
        self.enzyme_name = enzyme_name

        self.md_contacts = {}
        self.md_energies = {}
        self.hbonds = {}
        self.docking = {}
        self.structural_notes = {}

    def add_md_contact(self, position: int, frequency: float):
        self.md_contacts[int(position)] = {
            "frequency": float(frequency)
        }

    def add_md_energy(self, position: int, total_energy: float):
        self.md_energies[int(position)] = {
            "total_energy": float(total_energy)
        }

    def add_hbond(self, position: int, persistence: float):
        self.hbonds[int(position)] = {
            "persistence": float(persistence)
        }

    def add_docking_note(self, position: int, note: str):
        self.docking[int(position)] = {
            "note": note
        }

    def add_structural_note(self, position: int, note: str):
        self.structural_notes[int(position)] = {
            "note": note
        }

    def get_residue_context(self, position: int):
        position = int(position)

        return {
            "position": position,
            "case_study": self.name,
            "enzyme_name": self.enzyme_name,
            "md_contact": self.md_contacts.get(position),
            "md_energy": self.md_energies.get(position),
            "hbond": self.hbonds.get(position),
            "docking": self.docking.get(position),
            "structural_note": self.structural_notes.get(position),
        }

    def to_dict(self):
        return {
            "name": self.name,
            "enzyme_name": self.enzyme_name,
            "md_contacts": self.md_contacts,
            "md_energies": self.md_energies,
            "hbonds": self.hbonds,
            "docking": self.docking,
            "structural_notes": self.structural_notes,
        }