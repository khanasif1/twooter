from __future__ import annotations

import argparse
from datetime import datetime


FEED_KEYS = ["trending", "latest", "home", "explore"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Twooter CLI",
        epilog=(
            "Notes:\n"
            "- Use @username for user lookups; numeric IDs also accepted.\n"
            "- feeds -n limits results client-side.\n"
            f"- feeds keys: {', '.join(FEED_KEYS)}"
            "\n- auth whoami shows acting user's role and team info."
            "\n- auth token-info shows saved token type and expiry."
            "\n- On login failure, it notes the user may not exist, prompts to try the bot key (if set), then tries team_invite_code,"
            " and finally creates a team if needed. After creating a team, XDG config is updated with team_invite_code."
            "\n  Use -y and optionally --team-name/--affiliation/--member-name/--member-email for non-interactive flows."
        ),)
    p.add_argument("--config")
    p.add_argument("--debug", action="store_true")

    sub = p.add_subparsers(dest="command")

    def add_agent(sp):
        mg = sp.add_mutually_exclusive_group(required=False)
        mg.add_argument("--as", dest="as_user")
        mg.add_argument("--asindex", dest="as_index", type=int)

    login = sub.add_parser("login")
    lg = login.add_mutually_exclusive_group(required=False)
    lg.add_argument("--user")
    lg.add_argument("--index", type=int)
    login.add_argument("who", nargs="?")
    login.add_argument("-y", "--yes", action="store_true")
    login.add_argument("--team-name", dest="team_name")
    login.add_argument("--affiliation", dest="affiliation")
    login.add_argument("--member-name", dest="member_name")
    login.add_argument("--member-email", dest="member_email")

    users = sub.add_parser("users")
    users_sub = users.add_subparsers(dest="users_cmd", required=True)
    ug = users_sub.add_parser("get")
    ug.add_argument("identifier")
    ume = users_sub.add_parser("me")
    add_agent(ume)
    uup = users_sub.add_parser("update")
    add_agent(uup)
    uup.add_argument("--display-name", required=True)
    uup.add_argument("--bio", required=True)
    ua = users_sub.add_parser("activity")
    ua.add_argument("identifier")
    ufo = users_sub.add_parser("follows")
    ufo.add_argument("identifier")
    ufr = users_sub.add_parser("followers")
    ufr.add_argument("identifier")
    uf = users_sub.add_parser("follow")
    add_agent(uf)
    uf.add_argument("target")
    uu = users_sub.add_parser("unfollow")
    add_agent(uu)
    uu.add_argument("target")

    tw = sub.add_parser("twoots")
    tw_sub = tw.add_subparsers(dest="twoots_cmd", required=True)
    twc = tw_sub.add_parser("create")
    add_agent(twc)
    twc.add_argument("--content", required=True)
    twc.add_argument("--parent-id", type=int)
    twc.add_argument("--embed")
    twc.add_argument("--media", nargs="*")
    twg = tw_sub.add_parser("get")
    twg.add_argument("post_id", type=int)
    twr = tw_sub.add_parser("replies")
    twr.add_argument("post_id", type=int)
    twl = tw_sub.add_parser("like")
    add_agent(twl)
    twl.add_argument("post_id", type=int)
    twul = tw_sub.add_parser("unlike")
    add_agent(twul)
    twul.add_argument("post_id", type=int)
    twrp = tw_sub.add_parser("repost")
    add_agent(twrp)
    twrp.add_argument("post_id", type=int)
    twurp = tw_sub.add_parser("unrepost")
    add_agent(twurp)
    twurp.add_argument("post_id", type=int)
    twd = tw_sub.add_parser("delete")
    add_agent(twd)
    twd.add_argument("post_id", type=int)

    twe = tw_sub.add_parser("embed")
    twe.add_argument("post_id", type=int)

    twald = tw_sub.add_parser("allowed-link-domains")

    twrep = tw_sub.add_parser("report")
    add_agent(twrep)
    twrep.add_argument("post_id", type=int)
    twrep.add_argument("--reason", required=True)

    twvis = tw_sub.add_parser("visibility")
    add_agent(twvis)
    twvis.add_argument("post_id", type=int)
    twvis.add_argument("--visibility", required=True, choices=["default", "safe", "manually_hidden", "needs-review"])

    twpi = tw_sub.add_parser("prompt-injection")
    add_agent(twpi)
    twpi.add_argument("post_id", type=int)
    twpi.add_argument("--value", required=True, choices=["true", "false"], help="Enable or disable prompt injection flag")

    no = sub.add_parser("notifications")
    no_sub = no.add_subparsers(dest="notifications_cmd", required=True)
    nli = no_sub.add_parser("list")
    add_agent(nli)
    nur = no_sub.add_parser("unread")
    add_agent(nur)
    nco = no_sub.add_parser("count")
    add_agent(nco)
    ncu = no_sub.add_parser("count-unread")
    add_agent(ncu)
    nmr = no_sub.add_parser("mark-read")
    add_agent(nmr)
    nmr.add_argument("id", type=int)
    nmu = no_sub.add_parser("mark-unread")
    add_agent(nmu)
    nmu.add_argument("id", type=int)
    ndl = no_sub.add_parser("delete")
    add_agent(ndl)
    ndl.add_argument("id", type=int)
    ncl = no_sub.add_parser("clear")
    add_agent(ncl)

    tg = sub.add_parser("tags")
    tg_sub = tg.add_subparsers(dest="tags_cmd", required=True)
    tg_sub.add_parser("trending")
    tgl = tg_sub.add_parser("lookup")
    tgl.add_argument("name")
    tga = tg_sub.add_parser("latest")
    tga.add_argument("name")

    se = sub.add_parser("search")
    se.add_argument("query")

    _feed_keys_str = ", ".join(FEED_KEYS)
    fe = sub.add_parser(
        "feeds",
        description=(
            f"Available feed keys: {_feed_keys_str}. "
            "'home' and 'explore' require authentication (use --as/--asindex)."
        ),)
    add_agent(fe)
    fe.add_argument("key", nargs="?")
    fe.add_argument("--at")
    fe.add_argument("-n", "--n", type=int)
    fe.add_argument("--list", action="store_true", help="List available feeds instead of fetching one")

    co = sub.add_parser("competition")
    co_sub = co.add_subparsers(dest="competition_cmd", required=True)
    cot = co_sub.add_parser("team")
    add_agent(cot)
    cou = co_sub.add_parser("team-update")
    add_agent(cou)
    cou.add_argument("--name", required=True)
    cou.add_argument("--affiliation", required=True)
    com = co_sub.add_parser("members")
    add_agent(com)
    comc = co_sub.add_parser("member-create")
    add_agent(comc)
    comc.add_argument("--name", required=True)
    comc.add_argument("--email", required=True)
    comg = co_sub.add_parser("member-get")
    add_agent(comg)
    comg.add_argument("member_id", type=int)
    comu = co_sub.add_parser("member-update")
    add_agent(comu)
    comu.add_argument("member_id", type=int)
    comu.add_argument("--name", required=True)
    comu.add_argument("--email", required=True)
    comr = co_sub.add_parser("member-resend")
    add_agent(comr)
    comr.add_argument("member_id", type=int)
    comd = co_sub.add_parser("member-delete")
    add_agent(comd)
    comd.add_argument("member_id", type=int)
    couu = co_sub.add_parser("users")
    add_agent(couu)
    couu.add_argument("--q")
    couu.add_argument("--admins", choices=["true", "false"])
    cop = co_sub.add_parser("promote")
    add_agent(cop)
    cop.add_argument("target")
    cod = co_sub.add_parser("demote")
    add_agent(cod)
    cod.add_argument("target")
    cor = co_sub.add_parser("rotate-invite-code")
    add_agent(cor)
    covg = co_sub.add_parser("verify-get")
    covg.add_argument("token")
    covp = co_sub.add_parser("verify-post")
    covp.add_argument("--name", required=True)
    covp.add_argument("--email", required=True)
    covp.add_argument("--token", required=True)
    covp.add_argument("--consent", action="store_true")
    covp.add_argument("--student", action="store_true")
    covp.add_argument("--age18", action="store_true")

    au = sub.add_parser(
        "auth",
        description=(
            "Authentication and account operations.\n"
            "Subcommands: change-password, logout, register-team (create TEAM_ADMIN), whoami (show role/team), token-info (saved token deets)."
        ),)
    au_sub = au.add_subparsers(dest="auth_cmd", required=True)
    auc = au_sub.add_parser("change-password")
    add_agent(auc)
    auc.add_argument("--new-password", required=True)
    aul = au_sub.add_parser("logout")
    add_agent(aul)

    aur = au_sub.add_parser("register-team")
    rg = aur.add_mutually_exclusive_group(required=False)
    rg.add_argument("--user")
    rg.add_argument("--index", type=int)
    aur.add_argument("who", nargs="?")
    aur.add_argument("--team-name", required=True)
    aur.add_argument("--affiliation", required=True)
    aur.add_argument("--member-name")
    aur.add_argument("--member-email")

    auw = au_sub.add_parser("whoami")
    add_agent(auw)
    aut = au_sub.add_parser("token-info")
    add_agent(aut)

    return p.parse_args()
