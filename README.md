# Python Project (`pypo`)

A simple CLI tool to create project structures from YAML templates.

## Installation

```bash
# Install from PyPI (when published)
pip install pypo

# Install from source (development)
git clone <repo-url>
cd pypo
pip install -e ".[dev]"
```

## Quick Start

### 1. Create a Template

Create a YAML file describing your project structure:

```yaml
# my-web-project.yaml
name: "web-project"
description: "A simple web project structure"
version: "1.0"

structure:
  - name: "src"
    type: "directory"
    children:
      - name: "index.html"
        type: "file"
        content: |
          <!DOCTYPE html>
          <html>
          <head><title>Hello World</title></head>
          <body><h1>Welcome!</h1></body>
          </html>
      - name: "styles"
        type: "directory"
        children:
          - name: "main.css"
            type: "file"
      - name: "scripts"
        type: "directory"
        children:
          - name: "app.js"
            type: "file"
  - name: "README.md"
    type: "file"
    content: "# My Web Project"
```

### 2. Save the Template

```bash
pypo create web-project --path ./my-web-project.yaml
```

### 3. Initialize a New Project

```bash
pypo init web-project --output ./my-new-site
```

## Commands

| Command | Description |
|---------|-------------|
| `pypo create <name> --path <yaml>` | Import a YAML template |
| `pypo init <name> [--output <dir>]` | Scaffold a project |
| `pypo list [--archived]` | List all templates |
| `pypo source <name>` | Display template YAML |
| `pypo edit <name>` | Open template in editor |
| `pypo export <name> --output <path>` | Export template to file |
| `pypo duplicate <name> <new_name>` | Clone a template |
| `pypo delete <name>` | Remove a template |
| `pypo archive <name>` | Archive a template |

## Template YAML Format

```yaml
name: "template-name"           # Required: unique identifier
description: "Description"      # Optional: what this template creates
version: "1.0"                  # Optional: template version

structure:                       # Required: list of files/directories
  - name: "folder-name"
    type: "directory"
    children:                    # Nested items for directories
      - name: "file.txt"
        type: "file"
        content: "File content"  # Optional: initial file content
```

## Configuration

Templates are stored in `~/.pypo/templates/`

### Storage Structure

```
~/.pypo/
├── config.json       # Global settings
├── templates/        # Active templates
│   ├── template1.yaml
│   └── template2.yaml
└── archive/          # Archived templates
    └── old-template.yaml
```

## Development

```bash
# Clone and install
git clone <repo-url>
cd pypo
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/ --fix
```

## License

MIT License - see LICENSE file for details.
