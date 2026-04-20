"""CLI entry point — defines all user-facing commands."""

from typing import Optional

import click
from rich.console import Console

from opencode_sync import core
from opencode_sync import __version__

console = Console()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, "-V", "--version")
def main():
    """Sync OpenCode configuration across machines via a private GitHub repo."""


@main.command()
@click.option("--repo", "repo_url", default=None, metavar="SSH_URL",
              help="SSH URL of an existing GitHub repo (e.g. git@github.com:user/opencode-config.git)")
def init(repo_url: Optional[str]):
    """Initialize sync. Creates or connects to a private GitHub repo."""
    core.cmd_init(repo_url)


@main.command()
def push():
    """Push local config to remote. Pulls first if remote has changes."""
    core.cmd_push()


@main.command()
def pull():
    """Pull remote config and apply it locally."""
    core.cmd_pull()


@main.command()
def status():
    """Show sync status (local vs remote)."""
    core.cmd_status()


@main.command()
def diff():
    """Show diff between local config and remote."""
    core.cmd_diff()
