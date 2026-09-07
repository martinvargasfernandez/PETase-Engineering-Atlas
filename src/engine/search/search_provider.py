from abc import ABC, abstractmethod


class SearchProvider(ABC):
    """
    Base interface for search providers in the PETase Engineering Atlas.
    """

    @abstractmethod
    def search(self, query):
        """
        Search for elements matching the query.

        Args:
            query (str): The search query.

        Returns:
            list[SearchResult]: A list of search results.
        """
        pass
