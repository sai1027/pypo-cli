"""Export command - Export a template to an external file."""

import click
from pathlib import Path

from pp.core.storage import storage
from pp.utils.helpers import print_success, print_error, print_info


@click.command("export")
@click.argument("name")
@click.option(
    "--output", "-o",
    required=True,
    type=click.Path(path_type=Path),
    help="Output file path"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite if file already exists"
)
def export(name: str, output: Path, force: bool):
    """
    Export a template to a YAML file.
    
    Copies the template to an external location for sharing or backup.
    
    Examples:
    
        pp export my-web-project --output ./template.yaml
        
        pp export react-app -o ~/backups/react.yaml --force
    """
    # Check if template exists
    if not storage.template_exists(name):
        print_error(f"Template '{name}' not found.")
        print_info("Run 'pp list' to see available templates.")
        raise SystemExit(1)
    
    # Resolve output path
    output = output.resolve()
    
    # Check if output file exists
    if output.exists() and not force:
        print_error(f"File '{output}' already exists. Use --force to overwrite.")
        raise SystemExit(1)
    
    # Ensure parent directory exists
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # Export the template
    try:
        if storage.export_template(name, output):
            print_success(f"Template '{name}' exported successfully!")
            print_info(f"Saved to: {output}")
        else:
            print_error(f"Failed to export template.")
            raise SystemExit(1)
    except Exception as e:
        print_error(f"Failed to export template: {e}")
        raise SystemExit(1)
