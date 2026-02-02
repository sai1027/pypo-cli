"""Edit command - Modify a template in default editor."""

from __future__ import annotations

import click
import subprocess
import os
from pathlib import Path

from pypo.core.storage import storage
from pypo.core.config import config
from pypo.core.parser import parse_template, TemplateError
from pypo.utils.helpers import print_success, print_error, print_info, print_warning


@click.command("edit")
@click.argument("name")
@click.option(
    "--editor", "-e",
    default=None,
    help="Editor to use (default: from config or system default)"
)
def edit(name: str, editor: str | None):
    """
    Open a template in your default editor.
    
    After saving, the template is validated.
    
    Examples:
    
        pypo edit my-web-project
        
        pypo edit react-app --editor code
        
        pypo edit node-api -e vim
    """
    # Check if template exists
    if not storage.template_exists(name):
        print_error(f"Template '{name}' not found.")
        print_info("Run 'pypo list' to see available templates.")
        raise SystemExit(1)
    
    # Get template path
    template_path = storage.get_template_path(name)
    
    # Determine editor
    if editor is None:
        editor = config.get("editor")
    
    # Store original content for comparison
    original_content = template_path.read_text(encoding="utf-8")
    
    try:
        # Open in editor
        print_info(f"Opening '{name}' in {editor}...")
        
        if os.name == "nt":
            # Windows
            subprocess.run([editor, str(template_path)], shell=True)
        else:
            # Unix-like
            subprocess.run([editor, str(template_path)])
        
        # Wait for editor to close
        print_info("Validating changes...")
        
        # Validate the updated template
        new_content = template_path.read_text(encoding="utf-8")
        
        if new_content == original_content:
            print_info("No changes detected.")
            return
        
        try:
            parse_template(new_content)
            print_success(f"Template '{name}' updated and validated successfully!")
        except TemplateError as e:
            print_warning(f"Template has validation warnings: {e}")
            print_info("The file has been saved, but may not work correctly.")
        
    except FileNotFoundError:
        print_error(f"Editor '{editor}' not found.")
        print_info("Set a different editor with: pypo config set editor <editor>")
        raise SystemExit(1)
    except Exception as e:
        print_error(f"Failed to edit template: {e}")
        raise SystemExit(1)
