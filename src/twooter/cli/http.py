from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import requests
from requests.auth import HTTPBasicAuth

from .util import dump_http


def extract_token(resp: requests.Response) -> Tuple[str, Optional[str], Optional[int]]:
    token = None
    token_type = None
    expires_at = None

    data = {}
    try:
        data = resp.json()
    except Exception:
        pass

    tok = data.get("access_token") or data.get("token")
    if tok:
        token = tok
        token_type = data.get("token_type") or "Bearer"
        expires_in = data.get("expires_in")
        if isinstance(expires_in, (int, float)):
            import time
            expires_at = int(time.time() + int(expires_in))

    if not token:
        preferred = ("session", "access_token", "token")
        chosen_name = None
        for name in preferred:
            if name in resp.cookies:
                chosen_name = name
                token = resp.cookies.get(name)
                break
        if not token:
            for c in resp.cookies:
                chosen_name = c.name
                token = c.value
                break
        if token:
            token_type = f"Cookie:{chosen_name or 'session'}"

    if not token:
        raise ValueError("Login returned no recognisable token or session cookie.")
    return token, token_type, expires_at


class ApiSession:
    def __init__(self, base_url: str, caddy_user: Optional[str], caddy_pass: Optional[str], debug: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if caddy_user and caddy_pass:
            self.session.auth = HTTPBasicAuth(caddy_user, caddy_pass)
        self.debug = debug

    def url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    # HTTP POST, not making an actual post on the website :P
    def post(self, path: str, *, json_body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
        r = self.session.post(self.url(path), json=json_body, headers=headers)
        if self.debug:
            dump_http(r, note=f"{path} {'OK' if 200 <= r.status_code < 300 else 'RESP'}")
        return r

    # HTTP GET, idk how you could get confused with this one lol
    def get(self, path: str, *, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        r = self.session.get(self.url(path), headers=headers)
        if self.debug:
            dump_http(r, note=f"{path} {'OK' if 200 <= r.status_code < 300 else 'RESP'}")
        return r

