from typing import Any, Dict, Optional


class AuthAPI:
    def __init__(self, api_session):
        self._api = api_session
        self._base = "/auth"

    def login(self, username: str, password: str):
        return self._api.post(f"{self._base}/login", json_body={"username": username, "password": password})

    def register(self, username: str, display_name: str, password: str, invite_code: Optional[str] = None,
                 competition_bot_key: Optional[str] = None):
        if competition_bot_key:
            body = {
                "username": username,
                "display_name": display_name,
                "password": password,
                "competition_bot_key": competition_bot_key,
            }
        elif invite_code:
            body = {
                "username": username,
                "display_name": display_name,
                "password": password,
                "invite_code": invite_code,
            }
        else:
            body = {
                "username": username,
                "display_name": display_name,
                "password": password,
            }
        return self._api.post(f"{self._base}/register", json_body=body)

    def register_team(self, username: str, display_name: str, password: str, team_name: str, affiliation: str,
                      first_member_name: str, first_member_email: str):
        body = {
            "username": username,
            "display_name": display_name,
            "password": password,
            "team": {
                "name": team_name,
                "affiliation": affiliation,
                "first_member": {"name": first_member_name, "email": first_member_email},
            },
        }
        return self._api.post(f"{self._base}/register-team", json_body=body)

    def change_password(self, token_headers: Dict[str, str], new_password: str):
        return self._api.post(f"{self._base}/change-password", json_body={"new_password": new_password}, headers=token_headers)

    def logout(self, token_headers: Dict[str, str]):
        return self._api.post(f"{self._base}/logout", json_body={}, headers=token_headers)

