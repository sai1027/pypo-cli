"""Init command - Scaffold a project from a template."""

from pathlib import Path

import click

from pypo.core.generator import GeneratorError, generate_project
from pypo.core.parser import TemplateError, parse_template
from pypo.core.storage import storage
from pypo.utils.helpers import console, print_error, print_info, print_success


@click.command("init")
@click.argument("name")
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=".",
    help="Output directory (default: current directory)"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite existing files"
)
def init(name: str, output: Path, force: bool):
    """
    Initialize a new project from a saved template.
    
    Creates the folder structure defined in the template.
    
    Examples:
    
        pypo init my-web-project
        
        pypo init react-app --output ./new-project
        
        pypo init node-api -o ~/projects/my-api --force
    """
    # Check if template exists
    if not storage.template_exists(name):
        print_error(f"Template '{name}' not found.")
        print_info("Run 'pypo list' to see available templates.")
        raise SystemExit(1)
    
    # Resolve output path
    output = output.resolve()
    
    # Check if output directory exists and is not empty
    if output.exists() and any(output.iterdir()) and not force:
        print_error(f"Directory '{output}' is not empty. Use --force to overwrite.")
        raise SystemExit(1)
    
    try:
        # Load and parse template
        content = storage.get_template(name)
        template = parse_template(content)
        
        # Generate project structure
        print_info(f"Initializing project from template '{name}'...")
        
        files, dirs = generate_project(template, output)
        
        print_success("Project initialized successfully!")
        console.print("\n[bold]Created:[/bold]")
        console.print(f"  📁 {len(dirs)} directories")
        console.print(f"  📄 {len(files)} files")
        console.print(f"\n[bold]Location:[/bold] {output}")
        
        # Show created structure
        if len(files) <= 15:
            console.print("\n[bold]Files created:[/bold]")
            for f in files:
                rel_path = f.relative_to(output)
                console.print(f"  [dim]└─[/dim] {rel_path}")
        else:
            console.print(f"\n[dim]Run 'tree {output}' to see full structure.[/dim]")
        
    except TemplateError as e:
        print_error(f"Invalid template: {e}")
        raise SystemExit(1)
    except GeneratorError as e:
        print_error(f"Failed to generate project: {e}")
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        raise SystemExit(1)
