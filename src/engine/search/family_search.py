from engine.family_engine import FamilyEngine
from engine.search_result import SearchResult
from engine.search.search_provider import SearchProvider


class FamilySearch(SearchProvider):
    """
    Search by protein family name from family consensus data.
    """

    def __init__(self):
        self.family_engine = FamilyEngine()

    def search(self, query):
        query = str(query).strip().lower()
        if not query:
            return []

        results = []
        families = self.family_engine.get_families()

        for family in families:
            if query in family.lower():
                df = self.family_engine.get_family_positions(family)
                positions = df["position"].dropna().astype(int).tolist()

                results.append(
                    SearchResult(
                        result_type="family",
                        title=family,
                        subtitle="Family search",
                        payload={
                            "family_name": family,
                            "positions": positions,
                        },
                    )
                )

        return results
