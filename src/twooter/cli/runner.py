from __future__ import annotations

import re
import sys
from datetime import datetime
from typing import Optional

from .client import TwooterClient
from .config import Config
from .parser import parse_args
from .util import enable_requests_debug, json_print


def main() -> None:
    args = parse_args()
    if args.debug:
        enable_requests_debug()

    cfg = Config(args.config)
    client = TwooterClient(
        cfg.base_url,
        cfg.personas_db,
        cfg.tokens_db,
        cfg.teams_db,
        cfg.caddy_user,
        cfg.caddy_pass,
        cfg.login_path,
        cfg.register_path,
        cfg.team_invite_code,
        cfg.competition_bot_key,
        cfg.config_path,
        debug=args.debug,
    )

    def resolve_agent() -> Optional[str]:
        if getattr(args, "as_user", None):
            u, *_ = client._get_by_identifier(args.as_user)
            return u
        if getattr(args, "as_index", None) is not None:
            u, *_ = client._get_by_index(args.as_index)
            return u
        return None

    if getattr(args, "command", None):
        cmd = args.command

        if cmd == "login":
            user_opt = getattr(args, "user", None)
            index_opt = getattr(args, "index", None)
            who_opt = getattr(args, "who", None)

            import getpass

            def prompt_credentials(
                hint_username: str | None = None,
                error_detail: str | None = None,
            ) -> tuple[str, str, str, str, None]:
                if sys.stdin is None or not sys.stdin.isatty():
                    raise SystemExit(
                        "No valid persona found and interactive input is not available. "
                        "Please rerun with --user/--index or supply credentials interactively.")

                if error_detail:
                    print(error_detail)
                else:
                    print("Persona not found or personas.db is missing required columns.")
                print("Enter credentials to proceed with login/registration:")
                while True:
                    default = f" [{hint_username}]" if hint_username else ""
                    u = input(f"Username{default}: ").strip()
                    if not u and hint_username:
                        u = hint_username
                    if re.fullmatch(r"^[a-z0-9_.]+$", u or ""):
                        break
                    print("Username must match ^[a-z0-9_.]+$ -- try again.")
                while True:
                    e = input("Email: ").strip()
                    if e:
                        break
                    print("Email is required -- try again.")
                while True:
                    p1 = getpass.getpass("Password: ")
                    p2 = getpass.getpass("Confirm password: ")
                    if p1 and p1 == p2:
                        break
                    print("Passwords did not match or are empty -- try again.")
                return (u, p1, e, u, None)

            prompted = False
            try:
                if user_opt:
                    username, password, email, display_name, team_inv_code = client._get_by_identifier(user_opt)
                elif index_opt is not None:
                    username, password, email, display_name, team_inv_code = client._get_by_index(index_opt)
                elif who_opt is not None:
                    if who_opt.isdigit():
                        username, password, email, display_name, team_inv_code = client._get_by_index(int(who_opt))
                    else:
                        username, password, email, display_name, team_inv_code = client._get_by_identifier(who_opt)
                else:
                    raise SystemExit("Provide --user NAME, --index N, or positional WHO")
            except Exception as e:
                hint = None
                if isinstance(who_opt, str) and not who_opt.isdigit():
                    hint = who_opt
                elif isinstance(user_opt, str):
                    hint = user_opt
                try:
                    print(
                        f"[info] Will create a new personas DB at {client.personas.path} (backing up any incompatible existing DB).")
                except Exception:
                    pass
                # Include specific error details (e.g., missing columns) when available
                username, password, email, display_name, team_inv_code = prompt_credentials(hint, str(e))
                prompted = True
            if client.debug:
                if email is not None:
                    print(f"[debug] persona email={email}")
                if password is not None:
                    print(f"[debug] persona password={password}")
            invite_code = cfg.team_invite_code
            info = client.login(
                username=username,
                password=password,
                display_name=display_name,
                invite_code=invite_code,
                bot_key=cfg.competition_bot_key,
                try_register_on_403=True,
                auto_confirm=bool(getattr(args, "yes", False)),
                team_name=getattr(args, "team_name", None),
                affiliation=getattr(args, "affiliation", None),
                member_name=getattr(args, "member_name", None),
                member_email=getattr(args, "member_email", None),)
            if prompted:
                try:
                    client.personas.save_or_update_user(
                        username, password, email, display_name, team_inv_code)
                    if client.debug:
                        print(
                            f"[debug] saved persona for {username} -> {client.personas.path}")
                except Exception as _e:
                    if client.debug:
                        print(f"[debug] failed to save persona: {_e}")
            print(
                f"OK login: user={info['username']} token_saved=1 token_type={info['token_type']} "
                f"expires_at={info['expires_at'] or 'unknown'} token={info.get('token','unknown')}")
            if info.get("me_verified") is not None:
                print(f"me_verified={1 if info['me_verified'] else 0}")
            return

        if cmd == "users":
            sc = args.users_cmd
            if sc == "get":
                out = client.users.get(args.identifier)
            elif sc == "me":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for users me")
                out = client.users.me(u)
            elif sc == "update":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for users update")
                out = client.users.update_me(u, args.display_name, args.bio)
            elif sc == "activity":
                out = client.users.activity(args.identifier)
            elif sc == "follows":
                out = client.users.follows(args.identifier)
            elif sc == "followers":
                out = client.users.followers(args.identifier)
            elif sc == "follow":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for users follow")
                out = client.users.follow(u, args.target)
            elif sc == "unfollow":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for users unfollow")
                out = client.users.unfollow(u, args.target)
            else:
                raise SystemExit("Unknown users subcommand")
            json_print(out)
            return

        if cmd == "twoots":
            sc = args.twoots_cmd
            if sc == "create":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for twoots create")
                out = client.twoots.create(
                    u, args.content, parent_id=args.parent_id, embed=args.embed, media=args.media)
            elif sc == "get":
                out = client.twoots.get(args.post_id)
            elif sc == "replies":
                out = client.twoots.replies(args.post_id)
            elif sc == "like":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for twoots like")
                out = client.twoots.like(u, args.post_id)
            elif sc == "unlike":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for twoots unlike")
                out = client.twoots.unlike(u, args.post_id)
            elif sc == "repost":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for twoots repost")
                out = client.twoots.repost(u, args.post_id)
            elif sc == "unrepost":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for twoots unrepost")
                out = client.twoots.unrepost(u, args.post_id)
            elif sc == "delete":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for twoots delete")
                out = client.twoots.delete(u, args.post_id)
            else:
                raise SystemExit("Unknown twoots subcommand")
            json_print(out)
            return

        if cmd == "notifications":
            u = resolve_agent()
            if not u:
                raise SystemExit("--as or --asindex required for notifications")
            sc = args.notifications_cmd
            if sc == "list":
                out = client.notifications.list(u)
            elif sc == "unread":
                out = client.notifications.unread(u)
            elif sc == "count":
                out = client.notifications.count(u)
            elif sc == "count-unread":
                out = client.notifications.count_unread(u)
            elif sc == "mark-read":
                out = client.notifications.mark_read(u, args.id)
            elif sc == "mark-unread":
                out = client.notifications.mark_unread(u, args.id)
            elif sc == "delete":
                out = client.notifications.delete(u, args.id)
            elif sc == "clear":
                out = client.notifications.clear(u)
            else:
                raise SystemExit("Unknown notifications subcommand")
            json_print(out)
            return

        if cmd == "tags":
            sc = args.tags_cmd
            if sc == "trending":
                out = client.tags.trending()
            elif sc == "lookup":
                out = client.tags.lookup(args.name)
            elif sc == "latest":
                out = client.tags.latest(args.name)
            else:
                raise SystemExit("Unknown tags subcommand")
            json_print(out)
            return

        if cmd == "search":
            json_print(client.search.search(args.query))
            return

        if cmd == "feeds":
            at = None
            if getattr(args, "at", None):
                try:
                    at = datetime.fromisoformat(args.at)
                except Exception:
                    raise SystemExit(
                        "--at must be an ISO8601 timestamp, e.g., 2045-01-23T12:34:56")
            n = getattr(args, "n", None)
            u = resolve_agent()
            out = client.feeds.feed(args.key, at, u)
            if isinstance(n, int) and n > 0:
                if isinstance(out, list):
                    out = out[:n]
                elif isinstance(out, dict):
                    for key in ("data", "items", "results", "posts", "twoots"):
                        if key in out and isinstance(out[key], list):
                            out = {**out, key: out[key][:n]}
                            break
            json_print(out)
            return

        if cmd == "competition":
            sc = args.competition_cmd
            if sc == "team":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for competition team")
                out = client.competition.get(u)
            elif sc == "team-update":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for team-update")
                out = client.competition.team_update(u, args.name, args.affiliation)
            elif sc == "members":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for members")
                out = client.competition.team_members(u)
            elif sc == "member-create":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for member-create")
                out = client.competition.team_member_create(u, args.name, args.email)
            elif sc == "member-get":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for member-get")
                out = client.competition.team_member_get(u, args.member_id)
            elif sc == "member-update":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for member-update")
                out = client.competition.team_member_update(u, args.member_id, args.name, args.email)
            elif sc == "member-resend":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for member-resend")
                out = client.competition.team_member_resend(u, args.member_id)
            elif sc == "member-delete":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for member-delete")
                out = client.competition.team_member_delete(u, args.member_id)
            elif sc == "users":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for users")
                admins = None
                if getattr(args, "admins", None) == "true":
                    admins = True
                elif getattr(args, "admins", None) == "false":
                    admins = False
                out = client.competition.users(u, q=args.q, admins=admins)
            elif sc == "promote":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for promote")
                out = client.competition.promote(u, args.target)
            elif sc == "demote":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for demote")
                out = client.competition.demote(u, args.target)
            elif sc == "rotate-invite-code":
                u = resolve_agent()
                if not u:
                    raise SystemExit("--as or --asindex required for rotate-invite-code")
                out = client.competition.rotate_invite_code(u)
            elif sc == "verify-get":
                out = client.competition.verify_get(args.token)
            elif sc == "verify-post":
                out = client.competition.verify_post(
                    args.name, args.email, args.token, args.consent, args.student, args.age18)
            else:
                raise SystemExit("Unknown competition subcommand")
            json_print(out)
            return

        if cmd == "auth":
            sc = args.auth_cmd
            if sc == "register-team":
                user_opt = getattr(args, "user", None)
                index_opt = getattr(args, "index", None)
                who_opt = getattr(args, "who", None)
                if user_opt:
                    username, password, email, display_name, _ = client._get_by_identifier(user_opt)
                elif index_opt is not None:
                    username, password, email, display_name, _ = client._get_by_index(index_opt)
                elif who_opt is not None:
                    if who_opt.isdigit():
                        username, password, email, display_name, _ = client._get_by_index(int(who_opt))
                    else:
                        username, password, email, display_name, _ = client._get_by_identifier(who_opt)
                else:
                    raise SystemExit(
                        "Provide --user NAME, --index N, or positional WHO for register-team")

                member_name = getattr(args, "member_name", None) or (display_name or username)
                member_email = getattr(args, "member_email", None) or email
                if not member_email:
                    raise SystemExit(
                        "--member-email is required if persona has no email in DB")
                r = client.auth.register_team(
                    username=username,
                    display_name=display_name or username,
                    password=password,
                    team_name=args.team_name,
                    affiliation=args.affiliation,
                    first_member_name=member_name,
                    first_member_email=member_email,)
                if client.debug:
                    from .util import dump_http

                    dump_http(
                        r,
                        note=(
                            "/auth/register-team OK"
                            if 200 <= r.status_code < 300
                            else "/auth/register-team RESP"
                        ),)
                r.raise_for_status()
                info = client._persist_login(username, r)
                json_print(
                    {
                        "data": True,
                        "username": info["username"],
                        "token_type": info["token_type"],
                        "expires_at": info["expires_at"],
                    })
                return

            u = resolve_agent()
            if not u:
                raise SystemExit("--as or --asindex required for auth commands")
            if sc == "change-password":
                headers = client._auth_headers(u)
                r = client.auth.change_password(headers, args.new_password)
                r.raise_for_status()
                json_print({"data": True})
            elif sc == "logout":
                headers = client._auth_headers(u)
                r = client.auth.logout(headers)
                r.raise_for_status()
                json_print({"data": True})
            elif sc == "whoami":
                me = {}
                team = None
                try:
                    me = client.users.me(u)
                except Exception:
                    me = {"data": None}
                try:
                    team = client.competition.get(u)
                except Exception:
                    team = {"data": None}

                data = me.get("data") if isinstance(me, dict) else None
                username = data.get("username") if isinstance(data, dict) else None
                role = None
                if isinstance(data, dict):
                    role = data.get("role")
                tdata = team.get("data") if isinstance(team, dict) else None
                tname = tdata.get("name") if isinstance(tdata, dict) else None
                json_print({"data": {"username": username, "role": role, "team_name": tname}})
            elif sc == "token-info":
                headers = None
                try:
                    headers = client._auth_headers(u)
                except Exception:
                    pass
                info = client.tokens.get_info(u) or {"username": u, "has_token": False}
                json_print({"data": info, "headers": headers or {}})
            else:
                raise SystemExit("Unknown auth subcommand!!!")
