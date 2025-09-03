from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any
import http.client as http_client

# Just stuff to help debug a request
def enable_requests_debug() -> None:
    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)
    logging.getLogger("urllib3").propagate = True


def json_print(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def dump_http(resp, note: str = "") -> None:
    req = resp.request
    print("\n=== HTTP DEBUG START", note, "===")
    print(f">>> {req.method} {req.url}")
    for k, v in req.headers.items():
        print(f">>> {k}: {v}")
    if req.body:
        body = req.body if isinstance(req.body, (bytes, bytearray)) else str(req.body)
        if isinstance(body, (bytes, bytearray)):
            try:
                body = body.decode("utf-8", "replace")
            except Exception:
                body = repr(body)
        print(">>>")
        print(body[:2000])
    print(f"<<< {resp.status_code} {resp.reason}")
    for k, v in resp.headers.items():
        print(f"<<< {k}: {v}")
    try:
        txt = resp.text
    except Exception:
        txt = "<super secret stuff>"
    if txt:
        print("<<<")
        print(txt[:4000])
    print("=== HTTP DEBUG END ===\n")


# XDG helpers
def _xdg_dir(default_tail: str) -> Path:
    return Path.home() / default_tail


def xdg_config_home() -> Path:
    return _xdg_dir(".config")


def xdg_data_home() -> Path:
    return _xdg_dir(".local/share")


def xdg_state_home() -> Path:
    return _xdg_dir(".local/state")


def ensure_parent(path_like: str | Path) -> bool:
    try:
        Path(path_like).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

