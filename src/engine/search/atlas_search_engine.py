from engine.search.residue_search import ResidueSearch
from engine.search.family_search import FamilySearch


class AtlasSearchEngine:
    """
    Modular search engine for the PETase Engineering Atlas.
    """

    def __init__(self):
        self.search_modules = [
            ResidueSearch(),
            FamilySearch(),
        ]

    def search(self, query):
        results = []

        for module in self.search_modules:
            results.extend(
                module.search(query)
            )

        return results