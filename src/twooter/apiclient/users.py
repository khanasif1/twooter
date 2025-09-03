from typing import Any, Dict, Union


class UsersAPI:
    def __init__(self, api_session, headers_for_username):
        self._api = api_session
        self._headers_for = headers_for_username
        self._base = "/users"

    def _fmt_ident(self, ident: Union[str, int]) -> str:
        if isinstance(ident, int):
            return str(ident)
        s = str(ident).strip()
        # Treat purely numeric strings as IDs
        if s.isdigit():
            return s
        # Ensure '@' prefix for usernames, because that's what we decided on lol
        return s if s.startswith("@") else f"@{s}"

    def _extract_id(self, payload: Dict[str, Any]) -> int:
        """Try to extract a numeric user id from a GET /users/@name response."""
        if isinstance(payload, dict):
            data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
            if isinstance(data, dict) and "id" in data:
                try:
                    return int(data["id"])
                except Exception:
                    pass
        raise ValueError("Unable to resolve user id from response payload")

    def me(self, username: str) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/me", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def update_me(self, username: str, display_name: str, bio: str) -> Dict[str, Any]:
        r = self._api.post(
            f"{self._base}/me",
            json_body={"display_name": display_name, "bio": bio},
            headers=self._headers_for(username),
        )
        r.raise_for_status()
        return r.json()

    def get(self, username_or_id: Union[str, int]) -> Dict[str, Any]:
        ident = self._fmt_ident(username_or_id)
        r = self._api.get(f"{self._base}/{ident}")
        r.raise_for_status()
        return r.json()

    def activity(self, username_or_id: Union[str, int]) -> Dict[str, Any]:
        ident = self._fmt_ident(username_or_id)
        r = self._api.get(f"{self._base}/{ident}/activity")
        r.raise_for_status()
        return r.json()

    def follows(self, username_or_id: Union[str, int]) -> Dict[str, Any]:
        ident = self._fmt_ident(username_or_id)
        r = self._api.get(f"{self._base}/{ident}/follows")
        r.raise_for_status()
        return r.json()

    def followers(self, username_or_id: Union[str, int]) -> Dict[str, Any]:
        ident = self._fmt_ident(username_or_id)
        r = self._api.get(f"{self._base}/{ident}/followers")
        r.raise_for_status()
        return r.json()

    def follow(self, agent_username: str, target_username_or_id: Union[str, int]) -> Dict[str, Any]:
        # Follow/unfollow expect numeric id in path. Resolve if a username was provided.
        target_path = None
        if isinstance(target_username_or_id, int) or str(target_username_or_id).strip().isdigit():
            target_path = str(target_username_or_id)
        else:
            # Resolve @username -> id
            info = self.get(target_username_or_id)
            target_path = str(self._extract_id(info))
        r = self._api.post(
            f"{self._base}/{target_path}/follow",
            json_body={},
            headers=self._headers_for(agent_username),
        )
        r.raise_for_status()
        return r.json()

    def unfollow(self, agent_username: str, target_username_or_id: Union[str, int]) -> Dict[str, Any]:
        # Resolve to numeric id if needed
        target_path = None
        if isinstance(target_username_or_id, int) or str(target_username_or_id).strip().isdigit():
            target_path = str(target_username_or_id)
        else:
            info = self.get(target_username_or_id)
            target_path = str(self._extract_id(info))
        r = self._api.session.delete(
            self._api.url(f"{self._base}/{target_path}/follow"),
            headers=self._headers_for(agent_username),
        )
        if 200 <= r.status_code < 300:
            return r.json()
        r.raise_for_status()
        return r.json()
