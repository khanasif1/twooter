from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from .cli import TwooterClient, Config

@dataclass
class TwooterOptions:
    base_url: str
    personas_db: Optional[str] = None
    tokens_db: Optional[str] = None
    teams_db: Optional[str] = None
    caddy_user: Optional[str] = None
    caddy_pass: Optional[str] = None
    login_path: str = "/auth/login"
    register_path: str = "/auth/register"
    competition_bot_key: Optional[str] = None
    team_invite_code: Optional[str] = None
    debug: bool = False
    config_path: Optional[str] = None

    @staticmethod
    def from_env(*, base_url: Optional[str] = None, debug: Optional[bool] = None) -> "TwooterOptions":
        dbg = bool(debug) if debug is not None else False
        cfg = Config(None)
        return TwooterOptions(
            base_url=cfg.base_url,
            personas_db=cfg.personas_db,
            tokens_db=cfg.tokens_db,
            teams_db=cfg.teams_db,
            caddy_user=cfg.caddy_user,
            caddy_pass=cfg.caddy_pass,
            competition_bot_key=cfg.competition_bot_key,
            team_invite_code=cfg.team_invite_code,
            debug=dbg,
            config_path=cfg.config_path,
        )

class Twooter:
    def __init__(self, opts: TwooterOptions) -> None:
        self._opts = opts
        if not opts.personas_db or not opts.tokens_db or not opts.teams_db:
            raise ValueError("personas_db, tokens_db, and teams_db must be set; TwooterOptions.from_env to load <--> config.json")
        self._client = TwooterClient(
            base_url=opts.base_url,
            personas_db=opts.personas_db,
            tokens_db=opts.tokens_db,
            teams_db=opts.teams_db,
            caddy_user=opts.caddy_user,
            caddy_pass=opts.caddy_pass,
            login_path=opts.login_path,
            register_path=opts.register_path,
            default_invite=opts.team_invite_code,
            default_bot_key=opts.competition_bot_key,
            config_path=opts.config_path,
            debug=opts.debug,
        )
        self._agent: Optional[str] = None

    # ---------- auth/session ----------

    def login(
        self,
        username: str,
        password: str,
        *,
        display_name: Optional[str] = None,
        invite_code: Optional[str] = None,
        bot_key: Optional[str] = None,
        auto_create_if_missing: bool = True,
        team_name: Optional[str] = None,
        affiliation: Optional[str] = None,
        member_name: Optional[str] = None,
        member_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        info = self._client.login(
            username=username,
            password=password,
            display_name=display_name or username,
            invite_code=invite_code or self._opts.team_invite_code,
            bot_key=bot_key or self._opts.competition_bot_key,
            try_register_on_403=auto_create_if_missing,
            auto_confirm=True,
            team_name=team_name,
            affiliation=affiliation,
            member_name=member_name or display_name or username,
            member_email=member_email,
        )
        self._agent = username
        return info

    def logout(self) -> Dict[str, Any]:
        u = self._need_agent()
        headers = self._client._auth_headers(u)
        r = self._client.auth.logout(headers)
        r.raise_for_status()
        return {"data": True}

    def change_password(self, new_password: str) -> Dict[str, Any]:
        u = self._need_agent()
        headers = self._client._auth_headers(u)
        r = self._client.auth.change_password(headers, new_password)
        r.raise_for_status()
        return {"data": True}

    def use_agent(self, username: str) -> None:
        self._agent = username

    def whoami(self) -> Dict[str, Any]:
        u = self._need_agent()
        try:
            me = self._client.users.me(u)
        except Exception:
            me = {"data": None}
        try:
            team = self._client.competition.get(u)
        except Exception:
            team = {"data": None}

        data = me.get("data") if isinstance(me, dict) else None
        username = data.get("username") if isinstance(data, dict) else u
        email_verified = data.get("email_verified") if isinstance(data, dict) else None
        role = (data.get("role") if isinstance(data, dict) else None) or None
        team_data = team.get("data") if isinstance(team, dict) else None
        if role is None:
            role = "TEAM_ADMIN" if team_data else "COMPETITOR"
        return {"data": {"username": username, "role": role, "email_verified": email_verified, "team": team_data}}

    def token_info(self) -> Dict[str, Any]:
        u = self._need_agent()
        info = self._client.tokens.get_info(u) or {}
        if not info:
            return {"data": None}
        return {
            "data": {
                "username": info.get("username", u),
                "token_type": info.get("token_type"),
                "expires_at": info.get("expires_at"),
                "updated_at": info.get("updated_at"),
            }
        }

    # ---------- users endpoints ----------

    def user_get(self, identifier: str) -> Dict[str, Any]:
        return self._client.users.get(identifier)

    def user_me(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.users.me(u)

    def user_update_me(self, display_name: str, bio: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.users.update_me(u, display_name, bio)

    def user_activity(self, identifier: str) -> Dict[str, Any]:
        return self._client.users.activity(identifier)

    def user_follows(self, identifier: str) -> Dict[str, Any]:
        return self._client.users.follows(identifier)

    def user_followers(self, identifier: str) -> Dict[str, Any]:
        return self._client.users.followers(identifier)

    def user_follow(self, target: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.users.follow(u, target)

    def user_unfollow(self, target: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.users.unfollow(u, target)

    # ---------- twoots endpoints ----------

    def post(self, content: str, *, parent_id: Optional[int] = None, embed: Optional[str] = None, media: Optional[List[str]] = None) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.create(u, content, parent_id=parent_id, embed=embed, media=media)

    def post_get(self, post_id: int) -> Dict[str, Any]:
        return self._client.twoots.get(post_id)

    def post_replies(self, post_id: int) -> Dict[str, Any]:
        return self._client.twoots.replies(post_id)

    def post_like(self, post_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.like(u, post_id)

    def post_unlike(self, post_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.unlike(u, post_id)

    def post_repost(self, post_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.repost(u, post_id)

    def post_unrepost(self, post_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.unrepost(u, post_id)

    def post_delete(self, post_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.delete(u, post_id)

    def post_get_embed(self, post_id: int) -> Dict[str, Any]:
        return self._client.twoots.get_embed(post_id)

    def post_allowed_link_domains(self) -> Dict[str, Any]:
        return self._client.twoots.allowed_link_domains()

    def post_report(self, post_id: int, reason: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.report(u, post_id, reason)

    def post_set_visibility(self, post_id: int, visibility: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.set_visibility(u, post_id, visibility)

    def post_set_prompt_injection(self, post_id: int, value: bool) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.twoots.set_prompt_injection(u, post_id, value)

    # ---------- notifications endpoints ----------

    def notifications_list(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.list(u)

    def notifications_unread(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.unread(u)

    def notifications_count(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.count(u)

    def notifications_count_unread(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.count_unread(u)

    def notifications_mark_read(self, notif_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.mark_read(u, notif_id)

    def notifications_mark_unread(self, notif_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.mark_unread(u, notif_id)

    def notifications_delete(self, notif_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.delete(u, notif_id)

    def notifications_clear(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.notifications.clear(u)

    # ---------- tags endpoints ----------

    def tags_trending(self) -> Dict[str, Any]:
        return self._client.tags.trending()

    def tags_lookup(self, name: str) -> Dict[str, Any]:
        return self._client.tags.lookup(name)

    def tags_latest(self, name: str) -> Dict[str, Any]:
        return self._client.tags.latest(name)

    # ---------- search endpoint ----------

    def search(self, query: str) -> Dict[str, Any]:
        return self._client.search.search(query)

    # ---------- feeds endpoint ----------

    def feed(self, key: str, *, at_iso: Optional[str] = None, agent: Optional[str] = None, top_n: Optional[int] = None) -> Union[Dict[str, Any], List[Any]]:
        who = agent or self._agent
        at = None
        if at_iso:
            from datetime import datetime
            at = datetime.fromisoformat(at_iso)
        out = self._client.feeds.feed(key, at, who)
        if isinstance(top_n, int) and top_n > 0:
            if isinstance(out, list):
                return out[:top_n]
            if isinstance(out, dict):
                for k in ("data", "items", "results", "posts", "twoots"):
                    if k in out and isinstance(out[k], list):
                        out = {**out, k: out[k][:top_n]}
                        break
        return out

    def feeds_list(self, agent: Optional[str] = None) -> Dict[str, Any]:
        who = agent or self._agent
        return self._client.feeds.list(who)

    # ---------- competition endpoints ----------

    def comp_team(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.get(u)

    def comp_team_update(self, name: str, affiliation: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.team_update(u, name, affiliation)

    def comp_members(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.team_members(u)

    def comp_member_create(self, name: str, email: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.team_member_create(u, name, email)

    def comp_member_get(self, member_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.team_member_get(u, member_id)

    def comp_member_update(self, member_id: int, name: str, email: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.team_member_update(u, member_id, name, email)

    def comp_member_resend(self, member_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.team_member_resend(u, member_id)

    def comp_member_delete(self, member_id: int) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.team_member_delete(u, member_id)

    def comp_users(self, q: Optional[str] = None, admins: Optional[bool] = None) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.users(u, q=q, admins=admins)

    def comp_promote(self, target: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.promote(u, target)

    def comp_demote(self, target: str) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.demote(u, target)

    def comp_rotate_invite_code(self) -> Dict[str, Any]:
        u = self._need_agent()
        return self._client.competition.rotate_invite_code(u)

    def comp_verify_get(self, token: str) -> Dict[str, Any]:
        return self._client.competition.verify_get(token)

    def comp_verify_post(self, name: str, email: str, token: str, consent: bool,
                        student: bool, age18: bool,) -> Dict[str, Any]:
        return self._client.competition.verify_post(name, email, token, consent, student, age18)

    # ---------- personas.db management ----------

    def personas_add_user(self, username: str, password: str, email: str,
                          display_name: Optional[str] = None,
                          team_invite_code: Optional[str] = None) -> Dict[str, Any]:
        self._client.personas.save_or_update_user(username, password, email, display_name, team_invite_code)
        return {"data": True, "username": username}

    def personas_list_users(self) -> Dict[str, Any]:
        users = self._client.personas.list_users()
        return {"data": users}

    def personas_delete_user(self, identifier: str) -> Dict[str, Any]:
        ok = self._client.personas.delete_by_identifier(identifier)
        return {"data": ok, "identifier": identifier}

    # ---------- internals ----------

    def _need_agent(self) -> str:
        if not self._agent:
            raise RuntimeError("No agent set. Call login(...) or use_agent(username) first.")
        return self._agent


def new(*, base_url: Optional[str] = None, debug: Optional[bool] = None,
            use_env: bool = True, personas_db: Optional[str] = None,
            tokens_db: Optional[str] = None, teams_db: Optional[str] = None,
            caddy_user: Optional[str] = None, caddy_pass: Optional[str] = None,
            bot_key: Optional[str] = None, team_invite: Optional[str] = None,
        )-> Twooter:
    if use_env:
        options = TwooterOptions.from_env(base_url=base_url, debug=debug)
        if personas_db: options.personas_db = personas_db
        if tokens_db: options.tokens_db = tokens_db
        if teams_db: options.teams_db = teams_db
        if caddy_user is not None: options.caddy_user = caddy_user
        if caddy_pass is not None: options.caddy_pass = caddy_pass
        if bot_key is not None: options.competition_bot_key = bot_key
        if team_invite is not None:options.team_invite_code = team_invite
    else:
        if not base_url:
            raise ValueError("base_url is required when use_env=False")
        options = TwooterOptions(
            base_url=base_url,
            personas_db=personas_db,
            tokens_db=tokens_db,
            teams_db=teams_db,
            caddy_user=caddy_user,
            caddy_pass=caddy_pass,
            competition_bot_key=bot_key,
            team_invite_code=team_invite,
            debug=bool(debug),
        )
    return Twooter(options)
