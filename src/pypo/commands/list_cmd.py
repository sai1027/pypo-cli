"""List command - Display all templates."""

import click

from pypo.core.storage import storage
from pypo.core.parser import TemplateParser
from pypo.utils.helpers import print_info, create_template_table, console


@click.command("list")
@click.option(
    "--archived", "-a",
    is_flag=True,
    help="List archived templates instead of active"
)
@click.option(
    "--all", "show_all",
    is_flag=True,
    help="List both active and archived templates"
)
def list_templates(archived: bool, show_all: bool):
    """
    List all saved templates.
    
    Shows template names, descriptions, and versions.
    
    Examples:
    
        pypo list
        
        pypo list --archived
        
        pypo list --all
    """
    if show_all:
        _show_templates(active=True)
        console.print()
        _show_templates(active=False)
    else:
        _show_templates(active=not archived)


def _show_templates(active: bool = True):
    """Display templates in a table."""
    templates = storage.list_templates(archived=not active)
    label = "Active" if active else "Archived"
    
    if not templates:
        print_info(f"No {label.lower()} templates found.")
        if active:
            console.print("[dim]Create one with: pypo create <name> --path <yaml-file>[/dim]")
        return
    
    # Load template info for each
    template_info = []
    for name in templates:
        content = storage.get_template(name, archived=not active)
        if content:
            try:
                from pypo.core.parser import TemplateParser
                import yaml
                data = yaml.safe_load(content)
                info = TemplateParser.get_template_info(data)
                template_info.append(info)
            except Exception:
                template_info.append({
                    "name": name,
                    "description": "Unable to parse",
                    "version": "?"
                })
    
    table = create_template_table(template_info)
    table.title = f"{label} Templates"
    console.print(table)
