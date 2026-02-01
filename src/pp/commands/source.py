"""Source command - Display template YAML content."""

import click

from pp.core.storage import storage
from pp.utils.helpers import print_error, print_info, print_yaml


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
    
        pp source my-web-project
        
        pp source old-template --archived
        
        pp source my-template --raw
    """
    # Check if template exists
    if not storage.template_exists(name, archived=archived):
        location = "archive" if archived else "templates"
        print_error(f"Template '{name}' not found in {location}.")
        print_info("Run 'pp list' to see available templates.")
        raise SystemExit(1)
    
    # Get and display content
    content = storage.get_template(name, archived=archived)
    
    if raw:
        click.echo(content)
    else:
        print_yaml(content, title=f"Template: {name}")
