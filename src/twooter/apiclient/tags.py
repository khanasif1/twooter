from typing import Any, Dict


class TagsAPI:
    def __init__(self, api_session):
        self._api = api_session
        self._base = "/tags"

    def trending(self) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/trending")
        r.raise_for_status()
        return r.json()

    def lookup(self, name: str) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/lookup/{name}")
        r.raise_for_status()
        return r.json()

    def latest(self, name: str) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/lookup/{name}/latest")
        r.raise_for_status()
        return r.json()

