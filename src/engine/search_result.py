from dataclasses import dataclass


@dataclass
class SearchResult:
    """
    Generic search result returned by Atlas search engines.
    """

    result_type: str
    title: str
    subtitle: str
    payload: object

    def to_dict(self):
        return {
            "result_type": self.result_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "payload": self.payload,
        }