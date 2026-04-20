"""Tests for config and utils modules."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from opencode_sync import config
from opencode_sync.utils import copy_to_repo, copy_from_repo, DEFAULT_SYNC_PATHS


# ── config tests ──────────────────────────────────────────────────────────────

def test_config_roundtrip(tmp_path):
    config_file = tmp_path / "config.json"
    with patch("opencode_sync.config.TOOL_CONFIG_FILE", config_file):
        config.set_repo_url("git@github.com:user/repo.git")
        assert config.get_repo_url() == "git@github.com:user/repo.git"


def test_config_missing_returns_none(tmp_path):
    config_file = tmp_path / "nonexistent.json"
    with patch("opencode_sync.config.TOOL_CONFIG_FILE", config_file):
        assert config.get_repo_url() is None


# ── utils tests ───────────────────────────────────────────────────────────────

def test_copy_to_repo_file(tmp_path):
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    home.mkdir()
    repo.mkdir()

    src = home / ".config" / "opencode" / "opencode.json"
    src.parent.mkdir(parents=True)
    src.write_text('{"model": "test"}')

    with patch("opencode_sync.utils.Path.home", return_value=home):
        dest = copy_to_repo(src, repo)

    assert dest.exists()
    assert dest.read_text() == '{"model": "test"}'


def test_copy_to_repo_directory(tmp_path):
    home = tmp_path / "home"
    repo = tmp_path / "repo"
    home.mkdir()
    repo.mkdir()

    skills_dir = home / ".agents" / "skills"
    skills_dir.mkdir(parents=True)
    (skills_dir / "my-skill").mkdir()
    (skills_dir / "my-skill" / "SKILL.md").write_text("---\nname: my-skill\n---")

    with patch("opencode_sync.utils.Path.home", return_value=home):
        dest = copy_to_repo(skills_dir, repo)

    assert (dest / "my-skill" / "SKILL.md").exists()


def test_copy_from_repo(tmp_path):
    repo = tmp_path / "repo"
    dest_home = tmp_path / "home"
    repo.mkdir()
    dest_home.mkdir()

    # Put a file in the repo
    repo_file = repo / ".config" / "opencode" / "opencode.json"
    repo_file.parent.mkdir(parents=True)
    repo_file.write_text('{"synced": true}')

    copy_from_repo(repo, dest_home)

    real = dest_home / ".config" / "opencode" / "opencode.json"
    assert real.exists()
    assert json.loads(real.read_text())["synced"] is True
