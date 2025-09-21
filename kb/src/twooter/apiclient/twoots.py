from typing import Any, Dict, Optional


class TwootsAPI:
    def __init__(self, api_session, headers_for_username):
        self._api = api_session
        self._headers_for = headers_for_username
        self._base = "/twoots"

    def create(self, username: str, content: str, parent_id: Optional[int] = None,
               embed: Optional[str] = None, media: Optional[list[str]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"content": content, "parent_id": parent_id}
        if embed is not None:
            payload["embed"] = embed
        if media is not None:
            payload["media"] = media
        r = self._api.post(self._base + "/", json_body=payload, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def get(self, post_id: int) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/{post_id}/")
        r.raise_for_status()
        return r.json()

    def replies(self, post_id: int) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/{post_id}/replies")
        r.raise_for_status()
        return r.json()

    def get_embed(self, post_id: int) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/{post_id}/embed")
        r.raise_for_status()
        return r.json()

    def like(self, username: str, post_id: int) -> Dict[str, Any]:
        r = self._api.post(f"{self._base}/{post_id}/like", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def unlike(self, username: str, post_id: int) -> Dict[str, Any]:
        r = self._api.session.delete(self._api.url(f"{self._base}/{post_id}/like"), headers=self._headers_for(username))
        if 200 <= r.status_code < 300:
            return r.json()
        r.raise_for_status()
        return r.json()

    def repost(self, username: str, post_id: int) -> Dict[str, Any]:
        r = self._api.post(f"{self._base}/{post_id}/repost", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def unrepost(self, username: str, post_id: int) -> Dict[str, Any]:
        r = self._api.session.delete(self._api.url(f"{self._base}/{post_id}/repost"), headers=self._headers_for(username))
        if 200 <= r.status_code < 300:
            return r.json()
        r.raise_for_status()
        return r.json()

    def delete(self, username: str, post_id: int) -> Dict[str, Any]:
        r = self._api.session.delete(self._api.url(f"{self._base}/{post_id}/"), headers=self._headers_for(username))
        if 200 <= r.status_code < 300:
            return r.json()
        r.raise_for_status()
        return r.json()

    def allowed_link_domains(self) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/allowed-link-domains")
        r.raise_for_status()
        return r.json()

    def report(self, username: str, post_id: int, reason: str) -> Dict[str, Any]:
        r = self._api.post(
            f"{self._base}/{post_id}/report",
            json_body={"reason": reason},
            headers=self._headers_for(username),
        )
        r.raise_for_status()
        return r.json()

    def set_visibility(self, username: str, post_id: int, visibility: str) -> Dict[str, Any]:
        r = self._api.post(
            f"{self._base}/{post_id}/visibility",
            json_body={"visibility": visibility},
            headers=self._headers_for(username),
        )
        r.raise_for_status()
        return r.json()

    # Bit odd that this is exposed lol
    def set_prompt_injection(self, username: str, post_id: int, prompt_injection: bool) -> Dict[str, Any]:
        r = self._api.post(
            f"{self._base}/{post_id}/prompt-injection",
            json_body={"prompt_injection": prompt_injection},
            headers=self._headers_for(username),
        )
        r.raise_for_status()
        return r.json()
