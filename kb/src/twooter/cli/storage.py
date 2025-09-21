from __future__ import annotations

import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path as _FsPath
from typing import Any, Dict, Optional, Tuple

from .util import ensure_parent


class TokenStore:
    def __init__(self, path: str) -> None:
        self.path = path

    def _ensure(self) -> None:
        ensure_parent(self.path)
        conn = sqlite3.connect(self.path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens (
              username   TEXT PRIMARY KEY,
              token      TEXT NOT NULL,
              token_type TEXT,
              expires_at INTEGER,
              raw_json   TEXT,
              updated_at INTEGER NOT NULL
            )
            """)
        conn.commit()
        conn.close()

    def save(
        self,
        username: str,
        token: str,
        token_type: Optional[str],
        expires_at: Optional[int],
        raw_json: Dict[str, Any],
    ) -> None:
        self._ensure()
        conn = sqlite3.connect(self.path)
        conn.execute(
            """
            INSERT INTO tokens(username, token, token_type, expires_at, raw_json, updated_at)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(username) DO UPDATE SET
              token=excluded.token,
              token_type=excluded.token_type,
              expires_at=excluded.expires_at,
              raw_json=excluded.raw_json,
              updated_at=excluded.updated_at
            """,
            (username, token, token_type, expires_at, json.dumps(raw_json), int(time.time())),)
        conn.commit()
        conn.close()

    def get(self, username: str) -> Optional[Tuple[str, Optional[str]]]:
        if not os.path.exists(self.path):
            return None
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        cur.execute("SELECT token, token_type FROM tokens WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        return (row[0], row[1]) if row else None

    def get_info(self, username: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return None
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT token, token_type, expires_at, updated_at, raw_json FROM tokens WHERE username = ?",
                (username,),)
            row = cur.fetchone()
        finally:
            conn.close()
        if not row:
            return None
        token, token_type, expires_at, updated_at, raw_json = row
        try:
            raw = json.loads(raw_json) if raw_json else None
        except Exception:
            raw = None
        return {
            "username": username,
            "token_type": token_type,
            "expires_at": int(expires_at) if expires_at is not None else None,
            "updated_at": int(updated_at) if updated_at is not None else None,
            "has_token": bool(token),
            "raw": raw,
        }


class PersonasDB:
    def __init__(self, path: str) -> None:
        self.path = path

    @staticmethod
    def _table_has_columns(conn: sqlite3.Connection, table: str, cols: Tuple[str, ...]) -> Dict[str, bool]:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        present = {name: False for name in cols}
        for row in cur.fetchall():
            try:
                col_name = row[1]
            except Exception:
                continue
            if col_name in present:
                present[col_name] = True
        return present

    @staticmethod
    def _fetch_user_row(conn: sqlite3.Connection, where_sql: str, params: Tuple) -> Dict[str, Any]:
        wanted = ("username", "password", "email", "display_name", "team_invite_code")
        present = PersonasDB._table_has_columns(conn, "users", wanted)
        cols = [c for c in wanted if present.get(c)]
        if not all(k in cols for k in ("username", "password", "email")):
            cur2 = conn.cursor()
            try:
                cur2.execute("PRAGMA table_info(users)")
                actual_cols = [r[1] for r in cur2.fetchall()]
            except Exception:
                actual_cols = []
            missing = [c for c in ("username", "password", "email") if c not in cols]
            raise RuntimeError(
                "users table must have at least username, password, and email columns; "
                f"missing: {', '.join(missing) or 'unknown'}; present: {', '.join(actual_cols) or 'unknown'}")
        sql = f"SELECT {', '.join(cols)} FROM users {where_sql}"
        cur = conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        if not row:
            return {}
        return dict(zip(cols, row))

    def get_by_identifier(self, ident: str) -> Tuple[str, str, Optional[str], Optional[str], Optional[str]]:
        conn = sqlite3.connect(self.path)
        try:
            row = self._fetch_user_row(conn, "WHERE username = ? OR email = ?", (ident, ident))
        finally:
            conn.close()
        if not row:
            raise ValueError(f"User not found: {ident}")
        return (
            row["username"],
            row["password"],
            row.get("email"),
            row.get("display_name") or row["username"],
            row.get("team_invite_code"),)

    def get_by_index(self, idx: int) -> Tuple[str, str, Optional[str], Optional[str], Optional[str]]:
        if idx < 1:
            raise ValueError("Index must be 1-based")
        conn = sqlite3.connect(self.path)
        try:
            row = self._fetch_user_row(conn, "ORDER BY rowid LIMIT 1 OFFSET ?", (idx - 1,))
        finally:
            conn.close()
        if not row:
            raise ValueError(f"No such user index: {idx}")
        return (
            row["username"],
            row["password"],
            row.get("email"),
            row.get("display_name") or row["username"],
            row.get("team_invite_code"),)

    def _users_table_exists(self, conn: sqlite3.Connection) -> bool:
        cur = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users' LIMIT 1")
        return cur.fetchone() is not None

    def _users_schema_compatible(self, conn: sqlite3.Connection) -> bool:
        required = ("username", "password", "email")
        if not self._users_table_exists(conn):
            return True
        present = self._table_has_columns(conn, "users", required)
        return all(present.values())

    def ensure_minimal_schema(self, *, reset_if_incompatible: bool = False) -> None:
        conn = sqlite3.connect(self.path)
        try:
            if reset_if_incompatible and not self._users_schema_compatible(conn):
                try:
                    p = _FsPath(self.path)
                    bak = p.with_suffix(p.suffix + ".bak")
                    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
                    bak_ts = p.with_name(p.name + f".{ts}.bak")
                    try:
                        p.rename(bak_ts)
                    except Exception:
                        p.rename(bak)
                except Exception:
                    pass
                conn.close()
                conn = sqlite3.connect(self.path)

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT,
                    password TEXT NOT NULL,
                    email TEXT,
                    display_name TEXT,
                    team_invite_code TEXT,
                    created_at TEXT
                )
                """)
            conn.commit()
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def save_or_update_user(
        self,
        username: str,
        password: str,
        email: str,
        display_name: Optional[str] = None,
        team_invite_code: Optional[str] = None,
    ) -> None:
        self.ensure_minimal_schema(reset_if_incompatible=True)
        conn = sqlite3.connect(self.path)
        try:
            present = self._table_has_columns(
                conn,
                "users",
                ("username", "password", "email", "display_name", "team_invite_code", "created_at"),)
            cols, vals = [], []
            if present.get("created_at"):
                cols.append("created_at"); vals.append(datetime.now(timezone.utc).isoformat())
            cols.append("username"); vals.append(username)
            cols.append("password"); vals.append(password)
            if present.get("email"):
                cols.append("email"); vals.append(email)
            if present.get("display_name"):
                cols.append("display_name"); vals.append(display_name or username)
            if present.get("team_invite_code") and team_invite_code is not None:
                cols.append("team_invite_code"); vals.append(team_invite_code)
            try:
                conn.execute("DELETE FROM users WHERE username = ?", (username,))
            except Exception:
                pass
            placeholders = ",".join(["?"] * len(cols))
            sql = f"INSERT INTO users({','.join(cols)}) VALUES({placeholders})"
            conn.execute(sql, vals)
            conn.commit()
        finally:
            conn.close()

    def list_users(self) -> list[dict[str, Any]]:
        """Return all users with available columns.
        Columns returned when present: username, email, display_name, team_invite_code, created_at.
        Shouldn't need more lol
        """
        self.ensure_minimal_schema(reset_if_incompatible=True)
        conn = sqlite3.connect(self.path)
        try:
            wanted = ("username", "email", "display_name", "team_invite_code", "created_at")
            present = self._table_has_columns(conn, "users", wanted)
            cols = [c for c in wanted if present.get(c)]
            if not cols:
                return []
            cur = conn.cursor()
            cur.execute(f"SELECT {', '.join(cols)} FROM users ORDER BY rowid ASC")
            rows = cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]
        finally:
            conn.close()

    def delete_by_identifier(self, ident: str) -> bool:
        """Delete a user by username or email. Returns True if a row was deleted."""
        self.ensure_minimal_schema(reset_if_incompatible=True)
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.cursor()
            # Try username first, then email
            cur.execute("DELETE FROM users WHERE username = ?", (ident,))
            n = cur.rowcount or 0
            if n == 0:
                cur.execute("DELETE FROM users WHERE email = ?", (ident,))
                n = cur.rowcount or 0
            conn.commit()
            return n > 0
        finally:
            conn.close()

    def count_users(self) -> int:
        conn = sqlite3.connect(self.path)
        try:
            (cnt,) = conn.execute("SELECT COUNT(1) FROM users").fetchone()
            return int(cnt or 0)
        finally:
            conn.close()

    def sample_usernames(self, first: int = 10, last: int = 10) -> Dict[str, Any]:
        conn = sqlite3.connect(self.path)
        try:
            (cnt,) = conn.execute("SELECT COUNT(1) FROM users").fetchone()
            cnt = int(cnt or 0)
            if cnt == 0:
                return {"count": 0, "first": [], "last": []}
            if cnt <= first + last:
                rows = conn.execute("SELECT rowid, username FROM users ORDER BY rowid").fetchall()
                names = [r[1] for r in rows]
                return {"count": cnt, "first": names, "last": []}
            first_rows = conn.execute(
                "SELECT rowid, username FROM users ORDER BY rowid LIMIT ?",
                (first,),
            ).fetchall()
            last_rows = conn.execute(
                "SELECT rowid, username FROM users ORDER BY rowid DESC LIMIT ?",
                (last,),
            ).fetchall()
            first_names = [r[1] for r in first_rows]
            last_names = [r[1] for r in reversed(last_rows)]
            return {"count": cnt, "first": first_names, "last": last_names}
        finally:
            conn.close()
