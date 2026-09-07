from engine.engineering_interpreter import interpret_engineering_decision


class EngineeringDecision:
    """
    Combines global Atlas evidence with enzyme-specific CaseStudy evidence
    to support mutation prioritization.

    This class does not modify the Atlas Evidence Score.
    """

    def __init__(self, residue, case_context):
        self.residue = residue
        self.case_context = case_context
        self.result = self.evaluate()

    def evaluate(self):

        score = 0
        reasons = []

        atlas_score = self.residue.atlas_evidence_score

        if atlas_score is not None:
            score += atlas_score
            reasons.append("Global Atlas Evidence Score used as baseline.")

        md_contact = self.case_context.get("md_contact")

        if md_contact and md_contact.get("frequency", 0) >= 50:
            score += 2
            reasons.append("Persistent PET contact during molecular dynamics.")

        md_energy = self.case_context.get("md_energy")

        if md_energy and md_energy.get("total_energy", 0) <= -10:
            score += 2
            reasons.append("Favorable residue-PET interaction energy.")

        hbond = self.case_context.get("hbond")

        if hbond and hbond.get("persistence", 0) >= 20:
            score += 1
            reasons.append("Relevant hydrogen-bond persistence.")

        if score >= 8:
            priority = "High"

        elif score >= 5:
            priority = "Medium"

        else:
            priority = "Low"

        result = {
            "position": self.residue.position,
            "reference_residue": self.residue.reference_residue,
            "atlas_evidence_score": atlas_score,
            "case_study": self.case_context.get("case_study"),
            "enzyme_name": self.case_context.get("enzyme_name"),
            "engineering_score": score,
            "engineering_priority": priority,
            "reasons": reasons,
        }

        result["engineering_interpretation"] = (
            interpret_engineering_decision(result)
        )

        return result

    def to_dict(self):
        return self.result