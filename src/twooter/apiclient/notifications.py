from typing import Any, Dict


class NotificationsAPI:
    def __init__(self, api_session, headers_for_username):
        self._api = api_session
        self._headers_for = headers_for_username

    def list(self, username: str) -> Dict[str, Any]:
        r = self._api.get("/notifications", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def unread(self, username: str) -> Dict[str, Any]:
        r = self._api.get("/notifications/unread", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def count(self, username: str) -> Dict[str, Any]:
        r = self._api.get("/notifications/count", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def count_unread(self, username: str) -> Dict[str, Any]:
        r = self._api.get("/notifications/unread/count", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def mark_read(self, username: str, notification_id: int) -> Dict[str, Any]:
        r = self._api.post(f"/notifications/{notification_id}/mark-read", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def mark_unread(self, username: str, notification_id: int) -> Dict[str, Any]:
        r = self._api.post(f"/notifications/{notification_id}/mark-unread", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def delete(self, username: str, notification_id: int) -> Dict[str, Any]:
        r = self._api.session.delete(self._api.url(f"/notifications/{notification_id}"), headers=self._headers_for(username))
        if 200 <= r.status_code < 300:
            return r.json()
        r.raise_for_status()
        return r.json()

    def clear(self, username: str) -> Dict[str, Any]:
        r = self._api.session.delete(self._api.url("/notifications/clear"), headers=self._headers_for(username))
        if 200 <= r.status_code < 300:
            return r.json()
        r.raise_for_status()
        return r.json()

