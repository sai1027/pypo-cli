"""Delete command - Remove a template."""

import click

from pypo.core.storage import storage
from pypo.utils.helpers import confirm_action, print_error, print_info, print_success


@click.command("delete")
@click.argument("name")
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Skip confirmation prompt"
)
@click.option(
    "--archived", "-a",
    is_flag=True,
    help="Delete from archive instead of active templates"
)
def delete(name: str, force: bool, archived: bool):
    """
    Delete a template permanently.
    
    This action cannot be undone. Consider using 'pypo archive' instead.
    
    Examples:
    
        pypo delete my-old-project
        
        pypo delete old-template --force
        
        pypo delete archived-project --archived
    """
    location = "archive" if archived else "templates"
    
    # Check if template exists
    if not storage.template_exists(name, archived=archived):
        print_error(f"Template '{name}' not found in {location}.")
        print_info("Run 'pypo list' to see available templates.")
        raise SystemExit(1)
    
    # Confirm deletion
    if not force:
        msg = f"Are you sure you want to delete '{name}'? This cannot be undone."
        if not confirm_action(msg):
            print_info("Deletion cancelled.")
            return
    
    # Delete the template
    try:
        if storage.delete_template(name, archived=archived):
            print_success(f"Template '{name}' deleted successfully.")
        else:
            print_error("Failed to delete template.")
            raise SystemExit(1)
    except Exception as e:
        print_error(f"Failed to delete template: {e}")
        raise SystemExit(1)
