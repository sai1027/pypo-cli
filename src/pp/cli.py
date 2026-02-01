"""Main CLI entry point for Project Pilot."""

import click

from pp import __version__
from pp.commands import archive, create, delete, duplicate, edit, export, init, list_cmd, source


@click.group()
@click.version_option(version=__version__, prog_name="Project Pilot")
def main():
    """
    Project Pilot (pp) - Scaffold projects from YAML templates.
    
    Create reusable project templates and initialize new projects
    with a single command.
    
    Examples:
    
        pp create my-template --path ./template.yaml
        
        pp init my-template --output ./new-project
        
        pp list
    """
    pass


# Register all commands
main.add_command(create.create)
main.add_command(init.init)
main.add_command(list_cmd.list_templates)
main.add_command(source.source)
main.add_command(edit.edit)
main.add_command(export.export)
main.add_command(duplicate.duplicate)
main.add_command(delete.delete)
main.add_command(archive.archive)


if __name__ == "__main__":
    main()
