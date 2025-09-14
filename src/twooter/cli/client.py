from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

from ..apiclient import *
from .http import ApiSession, extract_token
from .storage import PersonasDB, TokenStore
from .util import dump_http, ensure_parent, xdg_config_home


class TwooterClient:
    def __init__(
        self,
        base_url: str,
        personas_db: str,
        tokens_db: str,
        teams_db: str,
        caddy_user: Optional[str],
        caddy_pass: Optional[str],
        login_path: str,
        register_path: str,
        default_invite: Optional[str],
        default_bot_key: Optional[str],
        config_path: Optional[str] = None,
        debug: bool = False,
    ) -> None:
        self.debug = debug
        self.api = ApiSession(base_url, caddy_user, caddy_pass, debug=debug)
        self.personas = PersonasDB(personas_db)
        self.tokens = TokenStore(tokens_db)
        self.default_invite = default_invite
        self.default_bot_key = default_bot_key
        self.config_path = config_path

        self.login_path = login_path
        self.register_path = register_path
        self.twoots_path = "/twoots"
        self.me_path = "/users/me"

        self.auth = AuthAPI(self.api)
        self.twoots = TwootsAPI(self.api, self._auth_headers)
        self.users = UsersAPI(self.api, self._auth_headers)
        self.notifications = NotificationsAPI(self.api, self._auth_headers)
        self.tags = TagsAPI(self.api)
        self.search = SearchAPI(self.api)
        self.feeds = FeedsAPI(self.api, self._auth_headers)
        self.competition = CompetitionAPI(self.api, self._auth_headers)

        # Can be debug here, but very nice to see where it's pulling a config/db
        # from!
        print(
            "--------\n\tconfig= {}\n\tlogin url= {}\n\tregister_url= {}\n\ttwoots_url= {}\n\tpersonas_db= {}\n\ttokens_db= {}\n\tbot_key_configured= {}\n--------\n".format(
                self.config_path,
                self.api.url(self.login_path),
                self.api.url(self.register_path),
                self.api.url(self.twoots_path),
                personas_db,
                tokens_db,
                bool(self.default_bot_key),
            ))

    def _update_config_team_invite_code(self, code: str) -> None:
        if self.config_path:
            target_path = Path(self.config_path).expanduser()
        else:
            xdg_target = (xdg_config_home() / "twooter" / "config.json").expanduser()
            target_path = xdg_target if ensure_parent(xdg_target) else (Path.cwd() / "config.json").resolve()
            ensure_parent(target_path)
        try:
            import json

            cfg: Dict[str, Any] = {}
            if target_path.exists():
                with open(target_path, "r", encoding="utf-8") as f:
                    try:
                        cfg = json.load(f)
                    except Exception:
                        cfg = {}
            if cfg.get("team_invite_code") == code:
                return
            cfg["team_invite_code"] = code
            if "base_url" not in cfg and getattr(self, "api", None):
                cfg["base_url"] = getattr(self.api, "base_url", None) or cfg.get("base_url") or ""
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            if self.debug:
                print(f"[debug] wrote team_invite_code to {target_path}")
        except Exception as e:
            if self.debug:
                print(f"[debug] failed to write team_invite_code to {target_path}: {e}")

    def _get_by_identifier(self, ident: str) -> Tuple[str, str, Optional[str], Optional[str], Optional[str]]:
        return self.personas.get_by_identifier(ident)

    def _get_by_index(self, n: int) -> Tuple[str, str, Optional[str], Optional[str], Optional[str]]:
        return self.personas.get_by_index(n)

    def _persist_login(self, username: str, resp: requests.Response) -> Dict[str, Any]:
        token, token_type, expires_at = extract_token(resp)
        raw = {}
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            try:
                raw = resp.json()
            except Exception:
                raw = {}
        self.tokens.save(username, token, token_type, expires_at, raw)
        if self.debug:
            print(
                f"[debug] saved token for {username}: type={token_type} expires_at={expires_at}")
        info = {
            "username": username,
            "token_type": token_type,
            "expires_at": expires_at,
            "token": token,
            "token_saved": True,
        }

        try:
            headers = self._auth_headers(username)
            r = self.api.get(self.me_path, headers=headers)
            ok = 200 <= r.status_code < 300
            if ok and r.headers.get("Content-Type", "").startswith("application/json"):
                data = r.json().get("data")
                ok = bool(data and data.get("username") == username)
            info["me_verified"] = bool(ok)
        except Exception:
            info["me_verified"] = False
        return info

    def rego_attempt(
        self,
        username: str,
        password: str,
        display_name: str,
        invite_code: Optional[str],
        bot_key: Optional[str],
        fallback_team_name: Optional[str],
    ) -> Optional[requests.Response]:
        r = self.auth.register(
            username=username,
            display_name=display_name,
            password=password,
            invite_code=(invite_code or fallback_team_name),
            competition_bot_key=bot_key,
        )
        if r.status_code in (200, 201, 409):
            return r
        return None

    def login(
        self,
        username: str,
        password: str,
        display_name: str,
        invite_code: Optional[str],
        bot_key: Optional[str],
        try_register_on_403: bool = True,
        auto_confirm: bool = False,
        team_name: Optional[str] = None,
        affiliation: Optional[str] = None,
        member_name: Optional[str] = None,
        member_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            resp = self.api.post(
                self.login_path, json_body={"username": username, "password": password})
            resp.raise_for_status()
            return self._persist_login(username, resp)
        except requests.HTTPError as e:
            r = e.response
            if self.debug and r is not None:
                dump_http(r, note="LOGIN ERROR")
            status = r.status_code if r is not None else None

            if (status in (401, 403, 404)) and try_register_on_403:
                print(
                    f"Login failed for '{username}' (status {status}). The user may not exist yet.")
                if not re.fullmatch(r"[a-z0-9_.]+", username or ""):
                    raise RuntimeError(
                        "Registration blocked: username is invalid! Use only lowercase letters, digits, underscores, and dots (regex: ^[a-z0-9_.]+).")

                chosen_bot = bot_key or self.default_bot_key
                chosen_inv = invite_code or self.default_invite

                used_bot = False
                if chosen_bot:
                    proceed = True if auto_confirm else (input("Attempt to register using bot key? [y/N] (N)").strip().lower() in ("y", "yes"))
                    if proceed:
                        print("Attempting registration using bot key...")
                        reg = self.rego_attempt(
                            username=username,
                            password=password,
                            display_name=display_name,
                            invite_code=None,
                            bot_key=chosen_bot,
                            fallback_team_name=None,)
                        if reg is not None:
                            if reg.status_code in (200, 201):
                                if self.debug:
                                    print(
                                        "[debug] bot-key registration OK; using register response token")
                                return self._persist_login(username, reg)
                            if reg.status_code == 409:
                                r2 = self.api.post(
                                    self.login_path,
                                    json_body={"username": username, "password": password},)
                                if self.debug:
                                    dump_http(
                                        r2,
                                        note=(
                                            "LOGIN RETRY OK"
                                            if 200 <= r2.status_code < 300
                                            else "LOGIN RETRY ERR"
                                        ),)
                                r2.raise_for_status()
                                return self._persist_login(username, r2)
                        used_bot = True

                if chosen_inv:
                    print(
                        "Bot key registration failed. Trying team invite code..."
                        if used_bot
                        else "Attempting registration using team invite code...")
                    reg = self.rego_attempt(
                        username=username,
                        password=password,
                        display_name=display_name,
                        invite_code=chosen_inv,
                        bot_key=None,
                        fallback_team_name=None,)
                    if reg is not None:
                        if reg.status_code in (200, 201):
                            if self.debug:
                                print(
                                    "[debug] invite-code registration OK; using register response token")
                            return self._persist_login(username, reg)
                        if reg.status_code == 409:
                            r2 = self.api.post(
                                self.login_path,
                                json_body={"username": username, "password": password},)
                            if self.debug:
                                dump_http(
                                    r2,
                                    note=(
                                        "LOGIN RETRY OK"
                                        if 200 <= r2.status_code < 300
                                        else "LOGIN RETRY ERR"
                                    ),)
                            r2.raise_for_status()
                            return self._persist_login(username, r2)

                print(
                    "Invite code registration failed or not configured. Creating a new team and registering...")
                default_team_name = team_name or username
                default_affiliation = affiliation or username
                default_member_name = member_name or (display_name or username)
                default_member_email = member_email
                if not default_member_email:
                    try:
                        _u, _p, _e, _dn, _ic = self.personas.get_by_identifier(username)
                        default_member_email = _e
                    except Exception:
                        default_member_email = None

                final_team_name = default_team_name
                final_affiliation = default_affiliation
                final_member_name = default_member_name
                final_member_email = default_member_email or ""
                if not auto_confirm:
                    if sys.stdin is None or not sys.stdin.isatty():
                        raise RuntimeError(
                            "Interactive input required for team creation. Use -y and provide --member-email.")
                    try:
                        tn = input(f"Team name [{default_team_name}]: ").strip()
                        if tn:
                            final_team_name = tn
                        af = input(f"Affiliation [{default_affiliation}]: ").strip()
                        if af:
                            final_affiliation = af
                        mn = input(f"First member name [{default_member_name}]: ").strip()
                        if mn:
                            final_member_name = mn
                        me = input(f"First member email [{default_member_email or ''}]: ").strip()
                        if me:
                            final_member_email = me
                    except EOFError:
                        pass
                if not final_member_email:
                    raise RuntimeError(
                        "Team creation cancelled: first member email is required!")

                try:
                    r = self.auth.register_team(
                        username=username,
                        display_name=display_name or username,
                        password=password,
                        team_name=final_team_name,
                        affiliation=final_affiliation,
                        first_member_name=final_member_name,
                        first_member_email=final_member_email,)
                    if self.debug:
                        dump_http(
                            r,
                            note=(
                                "/auth/register-team OK"
                                if 200 <= r.status_code < 300
                                else "/auth/register-team RESP"
                            ),)
                    r.raise_for_status()
                except requests.HTTPError as e:
                    status3 = (
                        e.response.status_code
                        if getattr(e, "response", None) is not None
                        else None )
                    if status3 == 400:
                        print(
                            f"Have you signed up with a .edu.au domain? ERR: {e}")
                        sys.exit(1)
                    raise
                info = self._persist_login(username, r)
                try:
                    team_info = self.competition.get(username) or {}
                    data = team_info.get("data") if isinstance(team_info, dict) else None
                    if isinstance(data, dict):
                        inv = data.get("invite_code")
                        if inv:
                            self._update_config_team_invite_code(inv)
                except Exception:
                    pass
                return info

            raise

    def _auth_headers(self, username: str) -> Dict[str, str]:
        tok = self.tokens.get(username)
        if not tok:
            raise RuntimeError(
                f"No token found for {username}. Run: twooter login {username}")
        token, token_type = tok
        if token_type and token_type.startswith("Cookie:"):
            cookie_name = token_type.split(":", 1)[1] or "session"
            return {"Cookie": f"{cookie_name}={token}"}
        return {"Authorization": f"Bearer {token}"}

    def create_post(
        self, username: str, content: str, parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        return self.twoots.create(username, content, parent_id=parent_id)

    def agent(self, username: str) -> Agent:
        return Agent(username, self.twoots, self.users, self.notifications)

