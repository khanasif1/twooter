from typing import Any, Dict, Optional


class CompetitionAPI:
    def __init__(self, api_session, headers_for_username):
        self._api = api_session
        self._headers_for = headers_for_username
        self._base = "/competition"
        # Team endpoints are under /competition/team
        self._team = f"{self._base}/team"

    # Public-ish (team admin role on user for get()):
    def get(self, username: Optional[str] = None) -> Dict[str, Any]:
        headers = self._headers_for(username) if username else None
        r = self._api.get(self._team, headers=headers)
        r.raise_for_status()
        return r.json()

    def verify_get(self, token: str) -> Dict[str, Any]:
        r = self._api.get(f"{self._base}/verify?token={token}")
        r.raise_for_status()
        return r.json()

    def verify_post(self, name: str, email: str, token: str,
                    consent: bool, is_student: bool, is_18: bool) -> Dict[str, Any]:
        body = {
            "name": name,
            "email": email,
            "token": token,
            "consents_to_experiment_according_to_ethics_document": consent,
            "is_australian_uni_student": is_student,
            "is_at_least_18_years_old": is_18,
        }
        r = self._api.post(f"{self._base}/verify", json_body=body)
        r.raise_for_status()
        return r.json()

    # Team-admin endpoints under /team
    def team_update(self, username: str, name: str, affiliation: str) -> Dict[str, Any]:
        r = self._api.post(f"{self._team}/", json_body={"name": name, "affiliation": affiliation}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def team_members(self, username: str) -> Dict[str, Any]:
        r = self._api.get(f"{self._team}/members", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def team_member_create(self, username: str, name: str, email: str) -> Dict[str, Any]:
        r = self._api.post(f"{self._team}/members", json_body={"name": name, "email": email}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def team_member_get(self, username: str, member_id: int) -> Dict[str, Any]:
        r = self._api.get(f"{self._team}/members/{member_id}", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def team_member_update(self, username: str, member_id: int, name: str, email: str) -> Dict[str, Any]:
        r = self._api.post(f"{self._team}/members/{member_id}", json_body={"name": name, "email": email}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def team_member_resend(self, username: str, member_id: int) -> Dict[str, Any]:
        r = self._api.post(f"{self._team}/members/{member_id}/resend-verification", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def team_member_delete(self, username: str, member_id: int) -> Dict[str, Any]:
        r = self._api.session.delete(self._api.url(f"{self._team}/members/{member_id}"), headers=self._headers_for(username))
        if 200 <= r.status_code < 300:
            return r.json()
        r.raise_for_status()
        return r.json()

    def users(self, username: str, q: Optional[str] = None, admins: Optional[bool] = None) -> Dict[str, Any]:
        params = []
        if q:
            params.append(f"q={q}")
        if admins is not None:
            params.append(f"admins={'true' if admins else 'false'}")
        qs = ("?" + "&".join(params)) if params else ""
        r = self._api.get(f"{self._team}/users{qs}", headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def promote(self, username: str, target_username: str) -> Dict[str, Any]:
        r = self._api.post(f"{self._team}/promote/{target_username}", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def demote(self, username: str, target_username: str) -> Dict[str, Any]:
        r = self._api.post(f"{self._team}/demote/{target_username}", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()

    def rotate_invite_code(self, username: str) -> Dict[str, Any]:
        r = self._api.post(f"{self._team}/rotate-invite-code", json_body={}, headers=self._headers_for(username))
        r.raise_for_status()
        return r.json()
