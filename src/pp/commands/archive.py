"""Archive command - Move template to archive."""

import click

from pp.core.storage import storage
from pp.utils.helpers import print_success, print_error, print_info


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
    
    Archived templates are hidden from 'pp list' but can be restored later.
    
    Examples:
    
        pp archive old-project
        
        pp archive my-template --restore
    """
    if restore:
        # Restore from archive
        if not storage.template_exists(name, archived=True):
            print_error(f"Template '{name}' not found in archive.")
            print_info("Run 'pp list --archived' to see archived templates.")
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
            print_info("Run 'pp list' to see available templates.")
            raise SystemExit(1)
        
        # Check if archived template with same name exists
        if storage.template_exists(name, archived=True):
            print_error(f"An archived template named '{name}' already exists.")
            print_info("Delete the archived version first with: pp delete {name} --archived")
            raise SystemExit(1)
        
        try:
            if storage.archive_template(name):
                print_success(f"Template '{name}' archived successfully!")
                print_info("Restore with: pp archive {name} --restore")
            else:
                print_error("Failed to archive template.")
                raise SystemExit(1)
        except Exception as e:
            print_error(f"Failed to archive template: {e}")
            raise SystemExit(1)
