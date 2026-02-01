"""YAML template parsing for Project Pilot."""

from pathlib import Path
from typing import Any, Optional
import yaml


class TemplateError(Exception):
    """Raised when a template is invalid."""
    pass


class TemplateParser:
    """Parse and validate YAML templates."""
    
    REQUIRED_FIELDS = ["name", "structure"]
    OPTIONAL_FIELDS = ["description", "version", "variables"]
    
    @staticmethod
    def load_from_file(path: Path) -> dict[str, Any]:
        """
        Load a template from a YAML file.
        
        Args:
            path: Path to the YAML file
            
        Returns:
            Parsed template as dictionary
            
        Raises:
            TemplateError: If file doesn't exist or is invalid YAML
        """
        if not path.exists():
            raise TemplateError(f"Template file not found: {path}")
        
        try:
            content = path.read_text(encoding="utf-8")
            return TemplateParser.load_from_string(content)
        except yaml.YAMLError as e:
            raise TemplateError(f"Invalid YAML: {e}")
    
    @staticmethod
    def load_from_string(content: str) -> dict[str, Any]:
        """
        Load a template from a YAML string.
        
        Args:
            content: YAML content as string
            
        Returns:
            Parsed template as dictionary
            
        Raises:
            TemplateError: If YAML is invalid
        """
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                raise TemplateError("Template must be a YAML dictionary")
            return data
        except yaml.YAMLError as e:
            raise TemplateError(f"Invalid YAML: {e}")
    
    @staticmethod
    def validate(template: dict[str, Any]) -> list[str]:
        """
        Validate a template structure.
        
        Args:
            template: Parsed template dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        for field in TemplateParser.REQUIRED_FIELDS:
            if field not in template:
                errors.append(f"Missing required field: '{field}'")
        
        # Validate structure if present
        if "structure" in template:
            if not isinstance(template["structure"], list):
                errors.append("'structure' must be a list")
            else:
                for i, item in enumerate(template["structure"]):
                    item_errors = TemplateParser._validate_structure_item(item, f"structure[{i}]")
                    errors.extend(item_errors)
        
        return errors
    
    @staticmethod
    def _validate_structure_item(item: dict, path: str) -> list[str]:
        """Validate a single structure item recursively."""
        errors = []
        
        if not isinstance(item, dict):
            return [f"{path}: must be a dictionary"]
        
        # Check required item fields
        if "name" not in item:
            errors.append(f"{path}: missing 'name' field")
        
        if "type" not in item:
            errors.append(f"{path}: missing 'type' field")
        elif item["type"] not in ["file", "directory"]:
            errors.append(f"{path}: 'type' must be 'file' or 'directory'")
        
        # Validate children for directories
        if item.get("type") == "directory" and "children" in item:
            if not isinstance(item["children"], list):
                errors.append(f"{path}.children: must be a list")
            else:
                for i, child in enumerate(item["children"]):
                    child_errors = TemplateParser._validate_structure_item(
                        child, f"{path}.children[{i}]"
                    )
                    errors.extend(child_errors)
        
        return errors
    
    @staticmethod
    def get_template_info(template: dict[str, Any]) -> dict[str, Any]:
        """
        Extract basic info from a template.
        
        Args:
            template: Parsed template dictionary
            
        Returns:
            Dictionary with name, description, version
        """
        return {
            "name": template.get("name", "Unknown"),
            "description": template.get("description", "No description"),
            "version": template.get("version", "1.0"),
        }


def parse_template(path_or_content: str | Path) -> dict[str, Any]:
    """
    Convenience function to parse a template.
    
    Args:
        path_or_content: File path or YAML content string
        
    Returns:
        Parsed and validated template
        
    Raises:
        TemplateError: If template is invalid
    """
    if isinstance(path_or_content, Path) or (
        isinstance(path_or_content, str) and Path(path_or_content).exists()
    ):
        template = TemplateParser.load_from_file(Path(path_or_content))
    else:
        template = TemplateParser.load_from_string(path_or_content)
    
    errors = TemplateParser.validate(template)
    if errors:
        raise TemplateError("Template validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return template
