"""Tests for Project Pilot CLI commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from pp.cli import main
from pp.core.storage import Storage


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage for testing."""
    return Storage(base_dir=tmp_path / ".pp")


@pytest.fixture
def sample_template(tmp_path):
    """Create a sample template file."""
    template_content = """
name: "test-project"
description: "A test project"
version: "1.0"

structure:
  - name: "src"
    type: "directory"
    children:
      - name: "main.py"
        type: "file"
        content: |
          print("Hello, World!")
  - name: "README.md"
    type: "file"
    content: "# Test Project"
"""
    template_path = tmp_path / "test_template.yaml"
    template_path.write_text(template_content)
    return template_path


class TestListCommand:
    """Tests for the list command."""
    
    def test_list_empty(self, runner):
        """Test listing when no templates exist."""
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0


class TestSourceCommand:
    """Tests for the source command."""
    
    def test_source_not_found(self, runner):
        """Test source with non-existent template."""
        result = runner.invoke(main, ["source", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestParser:
    """Tests for the template parser."""
    
    def test_parse_valid_template(self, sample_template):
        """Test parsing a valid template."""
        from pp.core.parser import parse_template
        
        template = parse_template(sample_template)
        assert template["name"] == "test-project"
        assert "structure" in template
    
    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML."""
        from pp.core.parser import parse_template, TemplateError
        
        with pytest.raises(TemplateError):
            parse_template("invalid: yaml: content: [")
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing fields."""
        from pp.core.parser import TemplateParser
        
        errors = TemplateParser.validate({})
        assert len(errors) >= 2
        assert any("name" in e for e in errors)
        assert any("structure" in e for e in errors)


class TestStorage:
    """Tests for the storage class."""
    
    def test_storage_init(self, temp_storage):
        """Test storage initialization creates directories."""
        assert temp_storage.base_dir.exists()
        assert temp_storage.templates_dir.exists()
        assert temp_storage.archive_dir.exists()
    
    def test_save_and_get_template(self, temp_storage):
        """Test saving and retrieving a template."""
        content = "name: test\nstructure: []"
        temp_storage.save_template("test", content)
        
        retrieved = temp_storage.get_template("test")
        assert retrieved == content
    
    def test_list_templates(self, temp_storage):
        """Test listing templates."""
        temp_storage.save_template("template1", "name: t1\nstructure: []")
        temp_storage.save_template("template2", "name: t2\nstructure: []")
        
        templates = temp_storage.list_templates()
        assert "template1" in templates
        assert "template2" in templates
    
    def test_delete_template(self, temp_storage):
        """Test deleting a template."""
        temp_storage.save_template("to_delete", "name: d\nstructure: []")
        assert temp_storage.template_exists("to_delete")
        
        temp_storage.delete_template("to_delete")
        assert not temp_storage.template_exists("to_delete")
    
    def test_archive_template(self, temp_storage):
        """Test archiving a template."""
        temp_storage.save_template("to_archive", "name: a\nstructure: []")
        temp_storage.archive_template("to_archive")
        
        assert not temp_storage.template_exists("to_archive", archived=False)
        assert temp_storage.template_exists("to_archive", archived=True)
    
    def test_duplicate_template(self, temp_storage):
        """Test duplicating a template."""
        original_content = "name: original\nstructure: []"
        temp_storage.save_template("original", original_content)
        temp_storage.duplicate_template("original", "copy")
        
        assert temp_storage.template_exists("copy")
        assert temp_storage.get_template("copy") == original_content


class TestGenerator:
    """Tests for the project generator."""
    
    def test_generate_simple_structure(self, tmp_path):
        """Test generating a simple structure."""
        from pp.core.generator import generate_project
        
        template = {
            "name": "test",
            "structure": [
                {"name": "src", "type": "directory"},
                {"name": "README.md", "type": "file", "content": "# Test"},
            ]
        }
        
        output_dir = tmp_path / "output"
        files, dirs = generate_project(template, output_dir)
        
        assert (output_dir / "src").is_dir()
        assert (output_dir / "README.md").is_file()
        assert (output_dir / "README.md").read_text() == "# Test"
    
    def test_generate_nested_structure(self, tmp_path):
        """Test generating nested directories."""
        from pp.core.generator import generate_project
        
        template = {
            "name": "test",
            "structure": [
                {
                    "name": "src",
                    "type": "directory",
                    "children": [
                        {"name": "main.py", "type": "file"},
                        {
                            "name": "lib",
                            "type": "directory",
                            "children": [
                                {"name": "utils.py", "type": "file"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        output_dir = tmp_path / "output"
        generate_project(template, output_dir)
        
        assert (output_dir / "src" / "main.py").is_file()
        assert (output_dir / "src" / "lib" / "utils.py").is_file()
