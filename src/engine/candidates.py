from engine.engineering_workspace import EngineeringWorkspace as CanonicalEngineeringWorkspace

class EngineeringWorkspace(CanonicalEngineeringWorkspace):
    """
    Legacy adapter for EngineeringWorkspace.
    
    Transforms the reports list returned by the canonical EngineeringWorkspace
    into the legacy dictionary format, without executing independent logic.
    """
    def run(self, limit_positions=50):
        # 1. Call the canonical EngineeringWorkspace
        reports = super().run(limit_positions=limit_positions)
        
        # 2. Transform the output reports list into the legacy dictionary format
        rows = []
        for report in reports:
            for proposal in report.proposals:
                row = proposal.to_dict()
                row["case_study"] = self.case_study_name
                # Note: The adapter does not evaluate or reconstruct case-study evidence
                # to strictly avoid duplicate logic. We use False as a legacy schema placeholder.
                row["has_case_evidence"] = False
                rows.append(row)
                
        # Preserve legacy sorting (highest proposal score first)
        rows = sorted(
            rows,
            key=lambda row: row.get("proposal_score", 0),
            reverse=True
        )
        
        # Preserve legacy summary counts
        high = sum(1 for row in rows if row.get("proposal_priority") == "High")
        medium = sum(1 for row in rows if row.get("proposal_priority") == "Medium")
        low = sum(1 for row in rows if row.get("proposal_priority") == "Low")
        
        return {
            "case_study": self.case_study_name,
            "positions_analyzed": len(reports),
            "mutation_proposals": len(rows),
            "high_priority": high,
            "medium_priority": medium,
            "low_priority": low,
            "top_candidates": rows[:20],
        }