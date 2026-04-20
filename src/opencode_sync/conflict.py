"""Interactive conflict resolution."""

from enum import Enum, auto

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


class Resolution(Enum):
    KEEP_LOCAL = auto()
    USE_REMOTE = auto()
    CANCEL = auto()


def prompt_conflict(diff: str) -> Resolution:
    """Show conflict info and prompt user to choose a resolution."""
    console.print(Panel(
        "[bold yellow]Conflict detected![/bold yellow]\n\n"
        "Remote has changes that conflict with your local state.\n"
        "You need to choose how to resolve this before syncing.",
        title="[red]Sync Conflict[/red]",
        border_style="red",
    ))

    choices = {
        "1": ("Keep local", "Push your local config and overwrite remote", Resolution.KEEP_LOCAL),
        "2": ("Use remote", "Pull remote config and discard local changes", Resolution.USE_REMOTE),
        "3": ("Show diff", None, None),
        "4": ("Cancel", "Do nothing", Resolution.CANCEL),
    }

    while True:
        console.print("\n[bold]Choose an option:[/bold]")
        for key, (label, desc, _) in choices.items():
            if desc:
                console.print(f"  [{key}] {label} — {desc}")
            else:
                console.print(f"  [{key}] {label}")

        choice = click.prompt("\nChoice", type=click.Choice(list(choices.keys())), show_choices=False)

        if choice == "3":
            if diff:
                console.print(Syntax(diff, "diff", theme="monokai"))
            else:
                console.print("[dim]No diff available.[/dim]")
            continue

        _, _, resolution = choices[choice]
        return resolution
