from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .util import xdg_config_home, xdg_data_home, xdg_state_home, ensure_parent


def resolve_db_path(
    config_value: Optional[str],
    default_name: str,
    base_dir: Path,
    *,
    prefer_state: bool = False,
) -> str:
    cfg_path = Path(config_value) if config_value else Path(default_name)
    if not cfg_path.is_absolute():
        cfg_path = base_dir / cfg_path
    cfg_path = cfg_path.expanduser()
    if cfg_path.exists():
        return str(cfg_path.resolve())
    xdg_base = xdg_state_home() if prefer_state else xdg_data_home()
    xdg_path = (xdg_base / "twooter" / default_name).expanduser()
    if xdg_path.exists():
        return str(xdg_path.resolve())
    ensure_parent(cfg_path)
    return str(cfg_path.resolve())


class Config:
    def __init__(self, config_path: Optional[str]) -> None:
        self.config_path = self._resolve_config_path(config_path)

        if not self.config_path or not Path(self.config_path).is_file():
            example = {
                "base_url": "https://social.legitreal.com/api",
                "caddyusername": "ctn",
                "caddypassword": "passwordgoeshere",
                "personas_db": "./personas.db",
                "tokens_db": "./tokens.db",
                "teams_db": "./teams.db",
                "competition_bot_key": "botkey",
                "team_invite_code": "teaminvitecode",
            }
            raise FileNotFoundError(
                "Config not found. Create ./config.json with fields: "
                + json.dumps(example, ensure_ascii=False))

        with open(self.config_path, encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        base_dir = Path(self.config_path).parent

        bu = data.get("base_url")
        if not bu:
            raise FileNotFoundError(
                "No base_url found in config. Create an XDG config at "
                f"{xdg_config_home()/ 'twooter' / 'config.json'} with " + '{"base_url":"https://..."}')
        self.base_url = bu.rstrip("/")

        self.personas_db = resolve_db_path(data.get("personas_db"), "personas.db", base_dir)
        self.tokens_db = resolve_db_path(data.get("tokens_db"), "tokens.db", base_dir, prefer_state=True)
        self.teams_db = resolve_db_path(data.get("teams_db"), "teams.db", base_dir)

        self.caddy_user = data.get("caddyusername")
        self.caddy_pass = data.get("caddypassword")
        self.competition_bot_key = data.get("competition_bot_key")
        self.team_invite_code = data.get("team_invite_code")

        self.login_path = "/auth/login"
        self.register_path = "/auth/register"

        for pth in (self.personas_db, self.tokens_db, self.teams_db):
            ensure_parent(pth)

    @staticmethod
    def _resolve_config_path(explicit: Optional[str]) -> Optional[str]:
        if explicit:
            return str(Path(explicit).expanduser())
        cwd_cfg = Path.cwd() / "config.json"
        if cwd_cfg.is_file():
            return str(cwd_cfg)
        xdg_cfg = xdg_config_home() / "twooter" / "config.json"
        if xdg_cfg.is_file():
            return str(xdg_cfg)
        return None

