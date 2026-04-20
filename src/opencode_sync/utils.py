"""Path helpers and shared utilities."""

import shutil
from pathlib import Path


# Paths that are synced by default (relative to home directory)
DEFAULT_SYNC_PATHS = [
    ".config/opencode/opencode.json",
    ".agents/skills",
    ".agents/.skill-lock.json",
]

# Where the tool stores its own state
TOOL_CONFIG_DIR = Path.home() / ".config" / "opencode-sync"
TOOL_CONFIG_FILE = TOOL_CONFIG_DIR / "config.json"
LOCAL_REPO_DIR = TOOL_CONFIG_DIR / "repo"


def expand(p: str) -> Path:
    """Expand ~ and env vars, return absolute Path."""
    return Path(p).expanduser().resolve()


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def copy_to_repo(src: Path, repo_dir: Path) -> Path:
    """Copy a file or directory from its real location into the repo mirror."""
    # Destination mirrors the path relative to home
    rel = src.relative_to(Path.home())
    dest = repo_dir / rel
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    elif src.exists():
        ensure_dir(dest.parent)
        shutil.copy2(src, dest)
    return dest


def copy_from_repo(repo_dir: Path, dest_home: Path = None) -> None:
    """Copy all tracked files from the repo mirror back to their real locations."""
    if dest_home is None:
        dest_home = Path.home()
    for rel_str in DEFAULT_SYNC_PATHS:
        repo_path = repo_dir / rel_str
        real_path = dest_home / rel_str
        if not repo_path.exists():
            continue
        if repo_path.is_dir():
            if real_path.exists():
                shutil.rmtree(real_path)
            shutil.copytree(repo_path, real_path)
        else:
            ensure_dir(real_path.parent)
            shutil.copy2(repo_path, real_path)
