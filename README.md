# Project Pilot (`pp`)

A powerful CLI tool for scaffolding projects from YAML templates.

## Installation

```bash
# Install from PyPI (when published)
pip install project-pilot

# Install from source (development)
git clone <repo-url>
cd project-pilot
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
pp create web-project --path ./my-web-project.yaml
```

### 3. Initialize a New Project

```bash
pp init web-project --output ./my-new-site
```

## Commands

| Command | Description |
|---------|-------------|
| `pp create <name> --path <yaml>` | Import a YAML template |
| `pp init <name> [--output <dir>]` | Scaffold a project |
| `pp list [--archived]` | List all templates |
| `pp source <name>` | Display template YAML |
| `pp edit <name>` | Open template in editor |
| `pp export <name> --output <path>` | Export template to file |
| `pp duplicate <name> <new_name>` | Clone a template |
| `pp delete <name>` | Remove a template |
| `pp archive <name>` | Archive a template |

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

Templates are stored in `~/.pp/templates/`

### Storage Structure

```
~/.pp/
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
cd project-pilot
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/ --fix
```

## License

MIT License - see LICENSE file for details.
