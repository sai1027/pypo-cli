"""Storage management for Python Project (pypo) templates."""

import json
import shutil
from pathlib import Path
from typing import Optional


class Storage:
    """Manages local storage of templates and configuration."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize storage with optional custom base directory.
        
        Args:
            base_dir: Custom base directory. Defaults to ~/.pypo/
        """
        self.base_dir = base_dir or Path.home() / ".pypo"
        self.templates_dir = self.base_dir / "templates"
        self.archive_dir = self.base_dir / "archive"
        self.config_file = self.base_dir / "config.json"
        
        # Ensure directories exist
        self._ensure_dirs()
    
    def _ensure_dirs(self) -> None:
        """Create storage directories if they don't exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.config_file.exists():
            self.config_file.write_text("{}", encoding="utf-8")
    
    def get_template_path(self, name: str, archived: bool = False) -> Path:
        """Get the path to a template file."""
        directory = self.archive_dir if archived else self.templates_dir
        return directory / f"{name}.yaml"
    
    def template_exists(self, name: str, archived: bool = False) -> bool:
        """Check if a template exists."""
        return self.get_template_path(name, archived).exists()
    
    def save_template(self, name: str, content: str) -> Path:
        """
        Save a template YAML file.
        
        Args:
            name: Template name (without .yaml extension)
            content: YAML content as string
            
        Returns:
            Path to the saved template
        """
        template_path = self.get_template_path(name)
        template_path.write_text(content, encoding="utf-8")
        return template_path
    
    def get_template(self, name: str, archived: bool = False) -> Optional[str]:
        """
        Get a template's content by name.
        
        Args:
            name: Template name
            archived: Look in archive instead of active templates
            
        Returns:
            Template content as string, or None if not found
        """
        template_path = self.get_template_path(name, archived)
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        return None
    
    def list_templates(self, archived: bool = False) -> list[str]:
        """
        List all template names.
        
        Args:
            archived: List archived templates instead of active
            
        Returns:
            List of template names (without .yaml extension)
        """
        directory = self.archive_dir if archived else self.templates_dir
        return sorted([p.stem for p in directory.glob("*.yaml")])
    
    def delete_template(self, name: str, archived: bool = False) -> bool:
        """
        Delete a template.
        
        Args:
            name: Template name to delete
            archived: Delete from archive instead of active
            
        Returns:
            True if deleted, False if not found
        """
        template_path = self.get_template_path(name, archived)
        if template_path.exists():
            template_path.unlink()
            return True
        return False
    
    def archive_template(self, name: str) -> bool:
        """
        Move a template to the archive.
        
        Args:
            name: Template name to archive
            
        Returns:
            True if archived, False if not found
        """
        source = self.get_template_path(name, archived=False)
        dest = self.get_template_path(name, archived=True)
        
        if source.exists():
            shutil.move(str(source), str(dest))
            return True
        return False
    
    def unarchive_template(self, name: str) -> bool:
        """
        Restore a template from the archive.
        
        Args:
            name: Template name to restore
            
        Returns:
            True if restored, False if not found
        """
        source = self.get_template_path(name, archived=True)
        dest = self.get_template_path(name, archived=False)
        
        if source.exists():
            shutil.move(str(source), str(dest))
            return True
        return False
    
    def duplicate_template(self, source_name: str, dest_name: str) -> bool:
        """
        Duplicate a template with a new name.
        
        Args:
            source_name: Name of template to copy
            dest_name: Name for the new copy
            
        Returns:
            True if duplicated, False if source not found
        """
        source = self.get_template_path(source_name)
        dest = self.get_template_path(dest_name)
        
        if source.exists():
            shutil.copy(str(source), str(dest))
            return True
        return False
    
    def get_config(self) -> dict:
        """Get global configuration."""
        if self.config_file.exists():
            return json.loads(self.config_file.read_text(encoding="utf-8"))
        return {}
    
    def save_config(self, config: dict) -> None:
        """Save global configuration."""
        self.config_file.write_text(
            json.dumps(config, indent=2), 
            encoding="utf-8"
        )
    
    def export_template(self, name: str, output_path: Path) -> bool:
        """
        Export a template to an external path.
        
        Args:
            name: Template name to export
            output_path: Destination path
            
        Returns:
            True if exported, False if not found
        """
        content = self.get_template(name)
        if content:
            output_path.write_text(content, encoding="utf-8")
            return True
        return False


# Global storage instance
storage = Storage()
