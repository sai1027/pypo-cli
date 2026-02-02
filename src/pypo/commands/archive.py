"""Archive command - Move template to archive."""

import click

from pypo.core.storage import storage
from pypo.utils.helpers import print_error, print_info, print_success


@click.command("archive")
@click.argument("name")
@click.option(
    "--restore", "-r",
    is_flag=True,
    help="Restore a template from archive instead of archiving"
)
def archive(name: str, restore: bool):
    """
    Archive or restore a template.
    
    Archived templates are hidden from 'pypo list' but can be restored later.
    
    Examples:
    
        pypo archive old-project
        
        pypo archive my-template --restore
    """
    if restore:
        # Restore from archive
        if not storage.template_exists(name, archived=True):
            print_error(f"Template '{name}' not found in archive.")
            print_info("Run 'pypo list --archived' to see archived templates.")
            raise SystemExit(1)
        
        # Check if active template with same name exists
        if storage.template_exists(name, archived=False):
            print_error(f"An active template named '{name}' already exists.")
            print_info("Delete or rename the active template first.")
            raise SystemExit(1)
        
        try:
            if storage.unarchive_template(name):
                print_success(f"Template '{name}' restored from archive!")
            else:
                print_error("Failed to restore template.")
                raise SystemExit(1)
        except Exception as e:
            print_error(f"Failed to restore template: {e}")
            raise SystemExit(1)
    else:
        # Archive the template
        if not storage.template_exists(name, archived=False):
            print_error(f"Template '{name}' not found.")
            print_info("Run 'pypo list' to see available templates.")
            raise SystemExit(1)
        
        # Check if archived template with same name exists
        if storage.template_exists(name, archived=True):
            print_error(f"An archived template named '{name}' already exists.")
            print_info(
                f"Delete the archived version first with: pypo delete {name} --archived"
            )
            raise SystemExit(1)
        
        try:
            if storage.archive_template(name):
                print_success(f"Template '{name}' archived successfully!")
                print_info("Restore with: pypo archive {name} --restore")
            else:
                print_error("Failed to archive template.")
                raise SystemExit(1)
        except Exception as e:
            print_error(f"Failed to archive template: {e}")
            raise SystemExit(1)
