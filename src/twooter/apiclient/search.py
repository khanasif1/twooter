from typing import Any, Dict
from urllib.parse import quote_plus


class SearchAPI:
    def __init__(self, api_session):
        self._api = api_session

    def search(self, query: str) -> Dict[str, Any]:
        q = quote_plus(query)
        r = self._api.get(f"/search?query={q}")
        r.raise_for_status()
        return r.json()
