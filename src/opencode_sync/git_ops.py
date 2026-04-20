"""Git operations wrapper around GitPython."""

from pathlib import Path
from typing import Optional

import git

from opencode_sync.utils import LOCAL_REPO_DIR, ensure_dir


def init_repo(repo_url: str) -> git.Repo:
    """Clone remote repo locally, or open if already cloned."""
    ensure_dir(LOCAL_REPO_DIR.parent)
    if (LOCAL_REPO_DIR / ".git").exists():
        return git.Repo(LOCAL_REPO_DIR)
    return git.Repo.clone_from(repo_url, LOCAL_REPO_DIR)


def open_repo() -> git.Repo:
    return git.Repo(LOCAL_REPO_DIR)


def is_initialized() -> bool:
    return (LOCAL_REPO_DIR / ".git").exists()


def commit_all(repo: git.Repo, message: str) -> Optional[git.Commit]:
    """Stage all changes and commit. Returns None if nothing to commit."""
    repo.git.add(A=True)
    if not repo.is_dirty(index=True, untracked_files=True):
        return None
    return repo.index.commit(message)


def push(repo: git.Repo) -> None:
    origin = repo.remote("origin")
    origin.push()


def fetch(repo: git.Repo) -> None:
    origin = repo.remote("origin")
    origin.fetch()


def has_remote_changes(repo: git.Repo) -> bool:
    """Return True if remote has commits not in local HEAD."""
    fetch(repo)
    local = repo.head.commit
    try:
        remote = repo.commit("origin/main")
    except git.BadName:
        remote = repo.commit("origin/master")
    return local != remote and repo.is_ancestor(local, remote)


def has_local_changes(repo: git.Repo) -> bool:
    """Return True if there are uncommitted local changes."""
    return repo.is_dirty(index=True, untracked_files=True)


def pull_ff(repo: git.Repo) -> bool:
    """Fast-forward pull. Returns True if updated, False if already up to date."""
    fetch(repo)
    local = repo.head.commit
    try:
        remote_ref = repo.remotes.origin.refs.main
    except AttributeError:
        remote_ref = repo.remotes.origin.refs.master
    if local == remote_ref.commit:
        return False
    repo.git.merge("--ff-only", remote_ref)
    return True


def get_diff(repo: git.Repo) -> str:
    """Return unified diff between local working tree and remote HEAD."""
    fetch(repo)
    try:
        remote_ref = "origin/main"
        repo.commit(remote_ref)
    except git.BadName:
        remote_ref = "origin/master"
    return repo.git.diff(remote_ref)


def create_local_repo(repo_url: str) -> git.Repo:
    """Init a new local repo, set remote, and do initial commit."""
    ensure_dir(LOCAL_REPO_DIR)
    repo = git.Repo.init(LOCAL_REPO_DIR)
    repo.create_remote("origin", repo_url)
    return repo
