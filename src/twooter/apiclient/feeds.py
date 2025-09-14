from datetime import datetime
from typing import Any, Dict, Optional


class FeedsAPI:
    def __init__(self, api_session, headers_for_username=None):
        self._api = api_session
        self._headers_for = headers_for_username

    def list(self, agent_username: Optional[str] = None) -> Dict[str, Any]:
        headers = None
        if self._headers_for is not None and agent_username:
            headers = self._headers_for(agent_username)
        r = self._api.get("/feeds/", headers=headers)
        r.raise_for_status()
        return r.json()

    def feed(self, key: str, at: Optional[datetime] = None, agent_username: Optional[str] = None) -> Dict[str, Any]:
        params = []
        if at is not None:
            params.append(f"at={at.isoformat()}")
        qs = ("?" + "&".join(params)) if params else ""
        headers = None
        if self._headers_for is not None and agent_username:
            headers = self._headers_for(agent_username)
        r = self._api.get(f"/feeds/{key}{qs}", headers=headers)
        r.raise_for_status()
        return r.json()
