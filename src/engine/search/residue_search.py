import re

from engine.residue import Residue
from engine.search_result import SearchResult
from engine.search.search_provider import SearchProvider


class ResidueSearch(SearchProvider):
    """
    Search by residue position, residue label or mutation label.
    """

    def search(self, query):
        query = str(query).strip().upper()

        if query == "":
            return []

        parsed = self._parse(query)

        if parsed is None:
            return []

        try:
            residue = Residue(parsed["position"])
        except ValueError:
            return []

        if parsed["type"] == "residue":
            if residue.reference_residue != parsed["reference"]:
                return []

        if parsed["type"] == "mutation":
            if residue.reference_residue != parsed["from_residue"]:
                return []

        return [
            SearchResult(
                result_type="residue",
                title=f"Residue {residue.position} ({residue.reference_residue})",
                subtitle=parsed["subtitle"],
                payload=residue,
            )
        ]

    def _parse(self, query):
        if query.isdigit():
            return {
                "type": "position",
                "position": int(query),
                "subtitle": "Position search",
            }

        match = re.match(r"^([A-Z])(\d+)$", query)

        if match:
            return {
                "type": "residue",
                "reference": match.group(1),
                "position": int(match.group(2)),
                "subtitle": "Residue search",
            }

        match = re.match(r"^([A-Z])(\d+)([A-Z])$", query)

        if match:
            mutation = query

            return {
                "type": "mutation",
                "from_residue": match.group(1),
                "position": int(match.group(2)),
                "to_residue": match.group(3),
                "subtitle": f"Mutation search: {mutation}",
            }

        return None