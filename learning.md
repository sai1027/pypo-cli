# Learning Guide: Building a Python CLI Library

This document covers all the essential concepts you need to understand for building a pip-installable CLI tool that manages user configurations and project scaffolding.

---

## Table of Contents

1. [Python Package Structure](#1-python-package-structure)
2. [pyproject.toml & Modern Packaging](#2-pyprojecttoml--modern-packaging)
3. [CLI Frameworks (Click)](#3-cli-frameworks-click)
4. [Where to Store User Data](#4-where-to-store-user-data)
5. [Global vs Local Configuration](#5-global-vs-local-configuration)
6. [YAML Parsing](#6-yaml-parsing)
7. [File System Operations](#7-file-system-operations)
8. [Entry Points & Console Scripts](#8-entry-points--console-scripts)
9. [Important Caveats & Best Practices](#9-important-caveats--best-practices)
10. [Development Workflow](#10-development-workflow)

---

## 1. Python Package Structure

### The `src` Layout (Recommended)

```
my-project/
├── pyproject.toml        # Package metadata
├── src/
│   └── mypackage/        # Your actual code
│       ├── __init__.py
│       └── module.py
└── tests/
    └── test_module.py
```

**Why `src/` layout?**
- Prevents accidental imports from local directory
- Ensures you're testing the installed version
- Cleaner separation of concerns

### The `__init__.py` File

```python
# src/pypo/__init__.py
__version__ = "0.1.0"
```

- Makes a directory a Python package
- Can export public API: `from pypo import create_project`
- Defines `__version__` for package versioning

---

## 2. pyproject.toml & Modern Packaging

### Why Not setup.py Anymore?

- **Old way**: `setup.py` (imperative, can execute arbitrary code)
- **New way**: `pyproject.toml` (declarative, standardized by PEP 517/518)

### Anatomy of pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "project-pilot"
version = "0.1.0"
description = "CLI tool for project scaffolding"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"}
]
dependencies = [
    "click>=8.0",
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black",
    "ruff",
]

[project.scripts]
pypo = "pypo.cli:main"  # This creates the 'pypo' command!

[tool.setuptools.packages.find]
where = ["src"]
```

### Key Sections Explained

| Section | Purpose |
|---------|---------|
| `[build-system]` | Tells pip how to build your package |
| `[project]` | Metadata (name, version, dependencies) |
| `[project.scripts]` | **Creates CLI commands** |
| `[tool.setuptools]` | Setuptools-specific config |

---

## 3. CLI Frameworks (Click)

### Why Click?

1. **Decorator-based** - Clean, readable code
2. **Automatic help generation**
3. **Type conversion** - `--count 5` becomes `int(5)`
4. **Composable** - Group commands easily
5. **Testing support** - Built-in test runner

### Basic Click Patterns

```python
import click

# Simple command
@click.command()
@click.argument('name')
@click.option('--count', '-c', default=1, help='Number of times')
def hello(name, count):
    """Say hello NAME for COUNT times."""
    for _ in range(count):
        click.echo(f'Hello, {name}!')

# Command group (subcommands)
@click.group()
def cli():
    """Python Project (pypo) - Scaffold projects from templates."""
    pass

@cli.command()
@click.argument('template_name')
@click.option('--path', '-p', required=True, type=click.Path(exists=True))
def create(template_name, path):
    """Create a new template from a YAML file."""
    click.echo(f'Creating template: {template_name}')

@cli.command()
def list():
    """List all templates."""
    click.echo('Templates: ...')

if __name__ == '__main__':
    cli()
```

### Click Decorators Cheat Sheet

| Decorator | Purpose |
|-----------|---------|
| `@click.command()` | Defines a command |
| `@click.group()` | Defines a command group |
| `@click.argument()` | Positional argument (required) |
| `@click.option()` | Optional flag/parameter |
| `@click.pass_context` | Pass Click context object |

### Option Types

```python
@click.option('--path', type=click.Path(exists=True))  # Must exist
@click.option('--output', type=click.Path())           # Any path
@click.option('--format', type=click.Choice(['json', 'yaml']))
@click.option('--verbose', is_flag=True)               # Boolean flag
@click.option('--config', type=click.File('r'))        # Open file
```

---

## 4. Where to Store User Data

This is **critical** for your CLI tool! You need to store templates and config somewhere.

### Cross-Platform User Directories

```python
from pathlib import Path

# User's home directory (cross-platform)
home = Path.home()

# Common patterns for CLI tools:
# 1. Hidden folder in home
config_dir = Path.home() / ".pypo"

# 2. Using platformdirs (recommended for production)
from platformdirs import user_data_dir, user_config_dir

data_dir = Path(user_data_dir("project-pilot", "YourName"))
config_dir = Path(user_config_dir("project-pilot", "YourName"))
```

### Platform-Specific Locations

| Platform | `~/.pypo/` resolves to |
|----------|----------------------|
| Windows | `C:\Users\<user>\.pypo\` |
| macOS | `/Users/<user>/.pypo/` |
| Linux | `/home/<user>/.pypo/` |

### Using `platformdirs` (Production-Ready)

```python
from platformdirs import user_data_dir, user_config_dir

# Windows: C:\Users\<user>\AppData\Local\project-pilot
# macOS:   ~/Library/Application Support/project-pilot  
# Linux:   ~/.local/share/project-pilot
data_dir = user_data_dir("project-pilot")

# For config files:
# Windows: C:\Users\<user>\AppData\Local\project-pilot
# macOS:   ~/Library/Preferences/project-pilot
# Linux:   ~/.config/project-pilot
config_dir = user_config_dir("project-pilot")
```

### Recommended Storage Structure

```
~/.pypo/
├── config.json           # Global settings
├── templates/            # Saved YAML templates
│   ├── web-project.yaml
│   ├── python-app.yaml
│   └── node-api.yaml
└── archive/              # Archived templates
    └── old-template.yaml
```

### Implementation Example

```python
# src/pypo/core/storage.py
from pathlib import Path
import json

class Storage:
    def __init__(self):
        self.base_dir = Path.home() / ".pypo"
        self.templates_dir = self.base_dir / "templates"
        self.archive_dir = self.base_dir / "archive"
        self.config_file = self.base_dir / "config.json"
        
        # Ensure directories exist
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create storage directories if they don't exist."""
        self.base_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        
        if not self.config_file.exists():
            self.config_file.write_text("{}")
    
    def save_template(self, name: str, content: str):
        """Save a template YAML file."""
        template_path = self.templates_dir / f"{name}.yaml"
        template_path.write_text(content)
    
    def get_template(self, name: str) -> str | None:
        """Get a template by name."""
        template_path = self.templates_dir / f"{name}.yaml"
        if template_path.exists():
            return template_path.read_text()
        return None
    
    def list_templates(self) -> list[str]:
        """List all template names."""
        return [p.stem for p in self.templates_dir.glob("*.yaml")]
```

---

## 5. Global vs Local Configuration

### Global Configuration

Stored in user's home directory. Applies everywhere.

```python
# ~/.pypo/config.json
{
    "default_output_dir": "~/Projects",
    "editor": "code",
    "author_name": "John Doe"
}
```

### Local Configuration (Per-Project)

Stored in the current project directory.

```python
# ./pypo.local.json (in project root)
{
    "template_name": "my-web-project",
    "created_at": "2025-01-15"
}
```

### Finding Local Config

```python
from pathlib import Path

def find_local_config():
    """Walk up directories to find local config."""
    current = Path.cwd()
    while current != current.parent:
        local_config = current / "pypo.local.json"
        if local_config.exists():
            return local_config
        current = current.parent
    return None
```

### Merging Configs (Local Overrides Global)

```python
import json

def get_config():
    """Get merged configuration (local overrides global)."""
    global_config = load_global_config()
    local_config = load_local_config() or {}
    
    # Local overrides global
    return {**global_config, **local_config}
```

### Environment Variable Override

```python
import os

def get_storage_dir():
    """Get storage directory with env override."""
    env_dir = os.environ.get("PYPO_STORAGE_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".pypo"
```

---

## 6. YAML Parsing

### Basic PyYAML Usage

```python
import yaml
from pathlib import Path

# Load YAML file
def load_template(path: Path) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# Save YAML file
def save_template(path: Path, data: dict):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

### YAML Template Structure for Project Scaffolding

```yaml
# template.yaml
name: "react-app"
description: "React application with TypeScript"
version: "1.0"

# Variables for templating
variables:
  project_name: "my-app"
  author: "Anonymous"

# The actual folder structure
structure:
  - name: "src"
    type: "directory"
    children:
      - name: "App.tsx"
        type: "file"
        content: |
          import React from 'react';
          export default function App() {
            return <div>Hello, {{ project_name }}!</div>;
          }
      - name: "index.tsx"
        type: "file"
  - name: "public"
    type: "directory"
    children:
      - name: "index.html"
        type: "file"
  - name: "package.json"
    type: "file"
    content: |
      {
        "name": "{{ project_name }}",
        "version": "1.0.0"
      }
```

### Validating YAML Structure

```python
def validate_template(data: dict) -> list[str]:
    """Validate template structure, return list of errors."""
    errors = []
    
    if 'name' not in data:
        errors.append("Missing 'name' field")
    if 'structure' not in data:
        errors.append("Missing 'structure' field")
    elif not isinstance(data['structure'], list):
        errors.append("'structure' must be a list")
    
    return errors
```

---

## 7. File System Operations

### Using pathlib (Modern Python)

```python
from pathlib import Path

# Create directories
base = Path("./new-project")
base.mkdir(parents=True, exist_ok=True)  # Like mkdir -p

# Create file with content
(base / "README.md").write_text("# My Project")

# Check existence
if (base / "package.json").exists():
    print("Already initialized!")

# List files
for file in base.glob("**/*.py"):  # Recursive glob
    print(file)

# Copy file
import shutil
shutil.copy(source, dest)

# Move file (for archive)
source.rename(dest)
```

### Generating Project Structure from YAML

```python
from pathlib import Path

def generate_structure(structure: list, base_path: Path):
    """Recursively generate folder structure."""
    for item in structure:
        item_path = base_path / item['name']
        
        if item['type'] == 'directory':
            item_path.mkdir(parents=True, exist_ok=True)
            if 'children' in item:
                generate_structure(item['children'], item_path)
        
        elif item['type'] == 'file':
            # Ensure parent directory exists
            item_path.parent.mkdir(parents=True, exist_ok=True)
            # Write content if provided
            content = item.get('content', '')
            item_path.write_text(content)
```

---

## 8. Entry Points & Console Scripts

### How `pypo` Becomes a Command

When you define this in `pyproject.toml`:

```toml
[project.scripts]
pypo = "pypo.cli:main"
```

It means:
1. Create an executable called `pypo`
2. When run, import `pypo.cli` module
3. Call the `main()` function

### The CLI Entry Point

```python
# src/pypo/cli.py
import click

@click.group()
@click.version_option()
def main():
    """Python Project (pypo) - Create projects from templates."""
    pass

@main.command()
def list():
    """List all templates."""
    click.echo("Templates...")

# Register other commands
from pypo.commands import create, init, source
main.add_command(create.create)
main.add_command(init.init)
main.add_command(source.source)
```

### After Installation

```bash
# Install in development mode
pip install -e .

# Now 'pypo' is available globally!
pypo --help
pypo list
pypo create my-template --path ./template.yaml
```

---

## 9. Important Caveats & Best Practices

### ⚠️ Common Pitfalls

#### 1. Hardcoded Paths
```python
# ❌ BAD - Won't work on Windows
config_path = "/home/user/.pp"

# ✅ GOOD - Cross-platform
config_path = Path.home() / ".pp"
```

#### 2. Not Creating Parent Directories
```python
# ❌ BAD - Fails if parent doesn't exist
path.mkdir()

# ✅ GOOD - Creates all parent directories
path.mkdir(parents=True, exist_ok=True)
```

#### 3. Using `yaml.load()` (Security Risk!)
```python
# ❌ BAD - Can execute arbitrary code!
data = yaml.load(content)

# ✅ GOOD - Safe loading
data = yaml.safe_load(content)
```

#### 4. Not Handling File Encoding
```python
# ❌ BAD - May fail with special characters
with open(path, 'r') as f:
    content = f.read()

# ✅ GOOD - Explicit encoding
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# ✅ ALSO GOOD - pathlib handles it
content = path.read_text(encoding='utf-8')
```

### ✅ Best Practices

#### 1. Confirm Destructive Actions
```python
@click.command()
@click.argument('name')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
def delete(name, force):
    """Delete a template."""
    if not force:
        click.confirm(f'Delete template "{name}"?', abort=True)
    # ... delete logic
```

#### 2. Provide Good Error Messages
```python
from rich.console import Console
console = Console()

def get_template(name: str):
    path = storage.templates_dir / f"{name}.yaml"
    if not path.exists():
        console.print(f"[red]Error:[/red] Template '{name}' not found.")
        console.print(f"[dim]Run 'pp list' to see available templates.[/dim]")
        raise SystemExit(1)
```

#### 3. Use Exit Codes
```python
import sys

# Success
sys.exit(0)

# General error
sys.exit(1)

# Or with Click
raise SystemExit(1)
```

#### 4. Validate Before Action
```python
def init_project(template_name: str, output_dir: Path):
    # Validate template exists
    if not template_exists(template_name):
        raise TemplateNotFoundError(template_name)
    
    # Validate output dir is empty
    if output_dir.exists() and any(output_dir.iterdir()):
        raise DirectoryNotEmptyError(output_dir)
    
    # Now safe to proceed
    ...
```

---

## 10. Development Workflow

### Initial Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Unix)
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Development Cycle

```bash
# Make changes to code...

# Test your command
pypo list
pypo create test --path ./template.yaml

# Run tests
pytest

# Format code
black src/
ruff check src/ --fix
```

### Testing CLI Commands

```python
# tests/test_cli.py
from click.testing import CliRunner
from pypo.cli import main

def test_list_command():
    runner = CliRunner()
    result = runner.invoke(main, ['list'])
    assert result.exit_code == 0
    assert 'Templates' in result.output

def test_create_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a test template file
        with open('test.yaml', 'w') as f:
            f.write('name: test\nstructure: []')
        
        result = runner.invoke(main, ['create', 'my-template', '--path', 'test.yaml'])
        assert result.exit_code == 0
```

### Publishing to PyPI (When Ready)

```bash
# Build distribution
python -m build

# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ project-pilot

# Upload to real PyPI
python -m twine upload dist/*
```

---

## Quick Reference Card

| Concept | Key Code |
|---------|----------|
| User home | `Path.home()` |
| Create dirs | `path.mkdir(parents=True, exist_ok=True)` |
| Read YAML | `yaml.safe_load(content)` |
| CLI command | `@click.command()` |
| CLI group | `@click.group()` |
| CLI argument | `@click.argument('name')` |
| CLI option | `@click.option('--flag', '-f')` |
| Entry point | `pypo = "pypo.cli:main"` in pyproject.toml |
| Dev install | `pip install -e .` |

---

## Next Steps

1. ✅ Read this guide
2. ⬜ Set up the package structure
3. ⬜ Implement `Storage` class
4. ⬜ Implement CLI commands one by one
5. ⬜ Add tests for each command
6. ⬜ Create example templates
7. ⬜ Write README documentation
