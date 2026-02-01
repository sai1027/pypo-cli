"""Create command - Import a YAML template."""

import click
from pathlib import Path

from pp.core.storage import storage
from pp.core.parser import parse_template, TemplateError
from pp.utils.helpers import print_success, print_error, print_info


@click.command("create")
@click.argument("name")
@click.option(
    "--path", "-p",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the YAML template file"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite if template already exists"
)
def create(name: str, path: Path, force: bool):
    """
    Create a new template from a YAML file.
    
    Imports a YAML template file and saves it to your local template storage.
    
    Examples:
    
        pp create my-web-project --path ./template.yaml
        
        pp create react-app -p ~/templates/react.yaml --force
    """
    # Check if template already exists
    if storage.template_exists(name) and not force:
        print_error(f"Template '{name}' already exists. Use --force to overwrite.")
        raise SystemExit(1)
    
    try:
        # Load and validate the template
        content = path.read_text(encoding="utf-8")
        template = parse_template(content)
        
        # Get template info for display
        template_name = template.get("name", name)
        description = template.get("description", "No description")
        
        # Save the template
        saved_path = storage.save_template(name, content)
        
        print_success(f"Template '{name}' created successfully!")
        print_info(f"  Name: {template_name}")
        print_info(f"  Description: {description}")
        print_info(f"  Stored at: {saved_path}")
        
    except TemplateError as e:
        print_error(f"Invalid template: {e}")
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Failed to create template: {e}")
        raise SystemExit(1)
