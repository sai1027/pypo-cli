"""Duplicate command - Clone a template."""

import click

from pypo.core.storage import storage
from pypo.utils.helpers import print_error, print_info, print_success


@click.command("duplicate")
@click.argument("source_name")
@click.argument("new_name")
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite if new name already exists"
)
def duplicate(source_name: str, new_name: str, force: bool):
    """
    Duplicate a template with a new name.
    
    Creates a copy of an existing template under a different name.
    
    Examples:
    
        pypo duplicate my-web-project my-web-project-v2
        
        pypo duplicate react-app react-app-typescript --force
    """
    # Check if source template exists
    if not storage.template_exists(source_name):
        print_error(f"Source template '{source_name}' not found.")
        print_info("Run 'pypo list' to see available templates.")
        raise SystemExit(1)
    
    # Check if destination already exists
    if storage.template_exists(new_name) and not force:
        print_error(f"Template '{new_name}' already exists. Use --force to overwrite.")
        raise SystemExit(1)
    
    # Delete existing if force
    if storage.template_exists(new_name) and force:
        storage.delete_template(new_name)
    
    # Duplicate the template
    try:
        if storage.duplicate_template(source_name, new_name):
            print_success("Template duplicated successfully!")
            print_info(f"  From: {source_name}")
            print_info(f"  To:   {new_name}")
        else:
            print_error("Failed to duplicate template.")
            raise SystemExit(1)
    except Exception as e:
        print_error(f"Failed to duplicate template: {e}")
        raise SystemExit(1)
