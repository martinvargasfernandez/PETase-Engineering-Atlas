class MutationRankingEngine:
    """
    Selects the best mutation proposal for each Atlas position.
    """

    def rank_by_position(self, proposals):
        grouped = {}

        for proposal in proposals:
            position = proposal.get("position")

            if position not in grouped:
                grouped[position] = []

            grouped[position].append(proposal)

        best = []

        for position, rows in grouped.items():
            rows = sorted(
                rows,
                key=lambda row: (
                    row.get("proposal_score", 0),
                    row.get("atlas_evidence_score", 0),
                ),
                reverse=True,
            )

            top = rows[0].copy()

            top["alternative_candidates"] = [
                row.get("candidate") for row in rows[1:]
            ]

            top["alternative_candidates_with_sources"] = [
                {
                    "candidate": row.get("candidate"),
                    "sources": row.get("sources", []),
                    "proposal_score": row.get("proposal_score", 0),
                    "proposal_priority": row.get("proposal_priority", "Low"),
                }
                for row in rows[1:]
            ]

            top["best_candidate_sources"] = top.get("sources", [])
            top["number_of_alternatives"] = len(rows) - 1

            best.append(top)

        best = sorted(
            best,
            key=lambda row: (
                row.get("proposal_score", 0),
                row.get("atlas_evidence_score", 0),
            ),
            reverse=True,
        )

        return best