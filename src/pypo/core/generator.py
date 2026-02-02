"""Project structure generator for Python Project (pypo)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class GeneratorError(Exception):
    """Raised when project generation fails."""
    pass


class ProjectGenerator:
    """Generate project folder structure from templates."""
    
    def __init__(self, template: dict[str, Any], output_dir: Path):
        """
        Initialize generator.
        
        Args:
            template: Parsed template dictionary
            output_dir: Directory to generate project in
        """
        self.template = template
        self.output_dir = output_dir
        self.variables = template.get("variables", {})
        self.created_files: list[Path] = []
        self.created_dirs: list[Path] = []
    
    def generate(self) -> tuple[list[Path], list[Path]]:
        """
        Generate the project structure.
        
        Returns:
            Tuple of (created_files, created_directories)
            
        Raises:
            GeneratorError: If generation fails
        """
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.created_dirs.append(self.output_dir)
        
        # Generate structure
        structure = self.template.get("structure", [])
        self._generate_items(structure, self.output_dir)
        
        return self.created_files, self.created_dirs
    
    def _generate_items(self, items: list[dict], parent_dir: Path) -> None:
        """Recursively generate structure items."""
        for item in items:
            name = item.get("name", "")
            item_type = item.get("type", "file")
            item_path = parent_dir / name
            
            if item_type == "directory":
                self._create_directory(item_path)
                # Recursively create children
                children = item.get("children", [])
                if children:
                    self._generate_items(children, item_path)
            else:  # file
                content = item.get("content", "")
                content = self._substitute_variables(content)
                self._create_file(item_path, content)
    
    def _create_directory(self, path: Path) -> None:
        """Create a directory."""
        path.mkdir(parents=True, exist_ok=True)
        self.created_dirs.append(path)
    
    def _create_file(self, path: Path, content: str = "") -> None:
        """Create a file with optional content."""
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.created_files.append(path)
    
    def _substitute_variables(self, content: str) -> str:
        """Replace {{ variable }} placeholders with values."""
        for key, value in self.variables.items():
            placeholder = "{{ " + key + " }}"
            content = content.replace(placeholder, str(value))
            # Also handle without spaces
            placeholder_no_space = "{{" + key + "}}"
            content = content.replace(placeholder_no_space, str(value))
        return content


def generate_project(
    template: dict[str, Any], 
    output_dir: Path,
    variables: dict[str, Any] | None = None
) -> tuple[list[Path], list[Path]]:
    """
    Convenience function to generate a project.
    
    Args:
        template: Parsed template dictionary
        output_dir: Directory to generate project in
        variables: Optional variable overrides
        
    Returns:
        Tuple of (created_files, created_directories)
    """
    if variables:
        # Merge provided variables with template variables
        template = template.copy()
        template["variables"] = {**template.get("variables", {}), **variables}
    
    generator = ProjectGenerator(template, output_dir)
    return generator.generate()
