"""Tool configuration (stored at ~/.config/opencode-sync/config.json)."""

import json
from pathlib import Path
from typing import Optional

from opencode_sync.utils import TOOL_CONFIG_FILE, ensure_dir


def load() -> dict:
    if TOOL_CONFIG_FILE.exists():
        return json.loads(TOOL_CONFIG_FILE.read_text())
    return {}


def save(data: dict) -> None:
    ensure_dir(TOOL_CONFIG_FILE.parent)
    TOOL_CONFIG_FILE.write_text(json.dumps(data, indent=2))


def get_repo_url() -> Optional[str]:
    return load().get("repo_url")


def set_repo_url(url: str) -> None:
    data = load()
    data["repo_url"] = url
    save(data)
