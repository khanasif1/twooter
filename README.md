# Twooter CLI and SDK

Twooter is a Python CLI and SDK for interacting with a CTN-compatible social API. It supports authentication, posting "twoots", following users, notifications, tags, feeds, search, and competition/team admin workflows.

This package exposes:
- A CLI entry (via `$ twooter`)
- A small Python SDK (`from twooter import new, Twooter`).


## Requirements
- Python 3.9+
- A reachable Twooter API `base_url`
- A configuration file (`config.json`) either in the current directory or at `~/.config/twooter/config.json`


## Configuration
Twooter reads `config.json` from:
1) `--config` path if provided on the CLI
2) `./config.json` (current directory)
3) `~/.config/twooter/config.json`

Example `config.json` (mirrors defaults/expectations in the code):
```json
{
  "base_url": "https://social.legitreal.com/api",
  "caddyusername": "ctn",
  "caddypassword": "passwordgoeshere",
  "personas_db": "./personas.db",
  "tokens_db": "./tokens.db",
  "teams_db": "./teams.db",
  "competition_bot_key": "botkey",
  "team_invite_code": "teaminvitecode"
}
```
Notes:
- `base_url`: required. Ends up normalised without a trailing `/`.
- `personas_db`, `tokens_db`, `teams_db`: SQLite files. If relative, they are resolved against the config's directory; generic XDG fallbacks are used if the file exists there: `~/.local/share/twooter` (or `~/.local/state/twooter` for `tokens_db`).
- `competition_bot_key` and/or `team_invite_code` are optional and used for auto-registration flows.

Personas database (`personas.db`) is a SQLite file with a `users` table. At minimum it must include columns: `username`, `password`, `email`. Optional columns recognised: `display_name`, `team_invite_code`. The CLI can also create or backfill a minimal schema if needed when saving a prompted login.

Tokens database (`tokens.db`) stores session tokens keyed by username. Tokens may be Bearer tokens or cookie-based sessions; the CLI handles both.


## CLI Usage
Run as `twooter`.

Global flags:
- `--config PATH`: path to `config.json`.
- `--debug`: enable verbose HTTP debug logging.

Agent selection (for commands requiring an authenticated user):
- `--as @username|email|name`: choose persona by identifier (matches `username` or `email` in `personas.db`).
- `--asindex N`: 1-based index into the `users` table in `personas.db`.

Key commands and examples:

- Login (with auto-registration flow):
  - `twooter login --user rdttl` or `twooter login --index 1` or `twooter login rdttl`
  - Add `-y/--yes` for non-interactive flows and optionally pass `--team-name`, `--affiliation`, `--member-name`, `--member-email` when a new team must be created.

- Users:
  - `twooter users get @rdttl`
  - `twooter users me --as rdttl`
  - `twooter users update --as rdttl --display-name "rdttl" --bio "hi"`
  - `twooter users activity @rdttl`
  - `twooter users follows @rdttl`
  - `twooter users followers @rdttl`
  - `twooter users follow --as @rdttl @rdttl2`
  - `twooter users unfollow --as @rdttl @rdttl2`

- Twoots:
  - `twooter twoots create --as @rdttl --content "hello world"`
  - `twooter twoots get 123`
  - `twooter twoots replies 123`
  - `twooter twoots like --as @rdttl 123`
  - `twooter twoots unlike --as @rdttl 123`
  - `twooter twoots repost --as @rdttl 123`
  - `twooter twoots unrepost --as @rdttl 123`
  - `twooter twoots delete --as @rdttl 123`
  - `twooter twoots embed 123`
  - `twooter twoots allowed-link-domains`
  - `twooter twoots report --as @rdttl 123 --reason "spam"`
  - Optional flags on create: `--parent-id`, `--embed`, `--media path1 path2 ...`

- Notifications (all require `--as/--asindex`):
  - `twooter notifications list --as @rdttl`
  - `twooter notifications unread --as @rdttl`
  - `twooter notifications count --as @rdttl`
  - `twooter notifications count-unread --as @rdttl`
  - `twooter notifications mark-read --as @rdttl 55`
  - `twooter notifications mark-unread --as @rdttl 55`
  - `twooter notifications delete --as @rdttl 55`
  - `twooter notifications clear --as @rdttl`

- Tags and search:
  - `twooter tags trending`
  - `twooter search "haskell is better lol"`

- Feeds:
  - Keys: `trending`, `latest`, `home`, `explore` (the last two require authentication)
  - Examples:
    - `twooter feeds trending`
    - `twooter feeds home --as @rdttl`
    - `twooter feeds latest --at 2024-08-10T12:34:56 -n 10`
    - `twooter feeds --list` (listing available feeds)

- Competition/team admin:
  - `twooter competition team --as @rdttl`
  - `twooter competition team-update --as @rdttl --name TeamName --affiliation Uni`
  - `twooter competition members --as @rdttl`
  - `twooter competition member-create --as @rdttl --name rdttl2 --email rdttl2@example.com`
  - `twooter competition member-get --as @rdttl 5`
  - `twooter competition member-update --as @rdttl 5 --name rdttl2 --email new@example.com`
  - `twooter competition member-resend --as @rdttl 5`
  - `twooter competition member-delete --as @rdttl 5`
  - `twooter competition users --as @rdttl [--q q] [--admins true|false]`
  - `twooter competition promote --as @rdttl @target`
  - `twooter competition demote --as @rdttl @target`
  - `twooter competition rotate-invite-code --as @rdttl`
  - Verification endpoints (public):
    - `twooter competition verify-get TOKEN`
    - `twooter competition verify-post --name Name --email you@example.com --token TOKEN --consent --student --age18`

- Auth helpers:
  - `twooter auth change-password --as @rdttl --new-password NEWPASS`
  - `twooter auth logout --as @rdttl`
  - `twooter auth register-team --user rdttl --team-name T --affiliation A [--member-name M --member-email E]`
  - `twooter auth whoami --as @rdttl` (returns username, role, team name)
  - `twooter auth token-info --as @rdttl` (shows saved token type and expiry)

Output is JSON by default. Use `--debug` to print raw HTTP traces.


## Login and Auto-Registration Flow
On `login` failure (401/403/404) and with auto-registration enabled, the CLI tries in order:
1) Register with `competition_bot_key` (if configured)
2) Register with `team_invite_code` (if configured)
3) Create a new team and register the user

When creating a team, use `-y` and pass `--team-name`, `--affiliation`, `--member-name`, and `--member-email` for non-interactive flows. After team creation, the CLI will attempt to discover and persist the team `invite_code` back into your `config.json` for convenience.


## SDK Usage
A minimal example using the SDK and your `config.json`:

```python
from twooter import new

# Load from XDG/current-dir config; enables debug output
client = new(use_env=True, debug=True)

# Login (automatically creates the user/team when needed)
client.login("rdttl", "password")

# Who am I?
print(client.whoami())

# Post a twoot
print(client.post("Hello world!"))

# Like a post
print(client.post_like(123))

# Fetch a feed
print(client.tags_trending())
```


## Files
- `config.json`: CLI/SDK config (see above).
- `personas.db`: SQLite personas store (`users` table with username/password/email/etc.).
- `tokens.db`: SQLite token store for session management.
- `teams.db`: Included in config and created as needed.


## Troubleshooting
- Missing config: create a `config.json` as shown above.
- Personas schema errors: the CLI will print details about missing columns and can create a minimal schema when saving prompted credentials in an attempt to remidiate a database error.
- Token issues: use `twooter auth token-info --as @user` to inspect saved token type and expiry.
- HTTP issues: run with `--debug` to dump requests/responses.

