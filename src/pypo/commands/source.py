"""Source command - Display template YAML content."""

import click

from pypo.core.storage import storage
from pypo.utils.helpers import print_error, print_info, print_yaml


@click.command("source")
@click.argument("name")
@click.option(
    "--archived", "-a",
    is_flag=True,
    help="Look in archived templates"
)
@click.option(
    "--raw", "-r",
    is_flag=True,
    help="Print raw YAML without formatting"
)
def source(name: str, archived: bool, raw: bool):
    """
    Display the source YAML of a template.
    
    Shows the full YAML content with syntax highlighting.
    
    Examples:
    
        pypo source my-web-project
        
        pypo source old-template --archived
        
        pypo source my-template --raw
    """
    # Check if template exists
    if not storage.template_exists(name, archived=archived):
        location = "archive" if archived else "templates"
        print_error(f"Template '{name}' not found in {location}.")
        print_info("Run 'pypo list' to see available templates.")
        raise SystemExit(1)
    
    # Get and display content
    content = storage.get_template(name, archived=archived)
    
    if raw:
        click.echo(content)
    else:
        print_yaml(content, title=f"Template: {name}")
