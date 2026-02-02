"""Utility helpers for Python Project (pypo)."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax


# Global console instance
console = Console()


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]![/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_yaml(content: str, title: str = "Template") -> None:
    """Print YAML content with syntax highlighting."""
    syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title, border_style="blue"))


def create_template_table(templates: list[dict]) -> Table:
    """Create a rich table for displaying templates."""
    table = Table(title="Templates", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="dim")
    table.add_column("Version", justify="center")
    
    for t in templates:
        table.add_row(
            t.get("name", "Unknown"),
            t.get("description", "No description"),
            t.get("version", "1.0"),
        )
    
    return table


def confirm_action(message: str) -> bool:
    """Ask for confirmation."""
    from rich.prompt import Confirm
    return Confirm.ask(message)
