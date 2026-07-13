---
difficulty: easy
last_sent:
review_count: 0
tags:
  - python
  - uv
  - packaging
topic: fullstack
---

# Python Packaging with uv

`uv` (by Astral) is an extremely fast Python package manager written in Rust. It replaces `pip`, `pip-tools`, `virtualenv`, and `pyenv` with a single tool. It's 10–100x faster than pip and handles dependency resolution, virtual environments, Python installation, and project scripts.

## Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Project Initialization

```bash
uv init my-project
cd my-project
```

This creates:

```
my-project/
├── pyproject.toml
├── README.md
├── hello.py
└── .python-version
```

## pyproject.toml

The single source of truth for project metadata, dependencies, and scripts.

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A sample project"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "pydantic>=2.10.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[project.scripts]
serve = "uvicorn main:app --reload"
lint = "ruff check ."
typecheck = "mypy ."
```

## Virtual Environments

`uv` manages virtual environments automatically. No manual activation needed.

```bash
# Create a venv (auto-detected from pyproject.toml)
uv venv

# uv commands auto-use the project venv
uv add fastapi
uv run python main.py

# Explicit venv path
uv venv .venv --python 3.12
```

## Dependency Management

```bash
# Add a dependency (resolves + locks automatically)
uv add fastapi
uv add "pydantic>=2.0"
uv add pytest --dev  # dev-only dependency

# Remove a dependency
uv remove fastapi

# Sync all dependencies from lock file
uv sync

# Install without dev dependencies (production)
uv sync --no-dev

# Update all dependencies
uv lock --upgrade
uv sync
```

## uv.lock

A cross-platform lock file (like `package-lock.json` or `Cargo.lock`) that ensures reproducible installs.

```bash
# Regenerate lock file
uv lock

# Install from lock file (exact versions)
uv sync
```

The lock file is committed to version control. It pins exact versions and hashes for every platform.

## Python Version Management

```bash
# Install a specific Python version
uv python install 3.12.8

# List installed versions
uv python list

# Pin a project to a Python version
uv python pin 3.12.8
# Creates .python-version file

# Use a specific Python version for a command
uv run --python 3.11 python script.py
```

## Running Scripts and Tools

```bash
# Run a script defined in pyproject.toml
uv run serve

# Run a one-off tool without installing
uvx ruff check .
uvx black --check .
uvx mypy .

# Run the project's entry point
uv run python -m my_project
```

## Publishing

```bash
# Build the package
uv build

# Publish to PyPI
uv publish --token $PYPI_TOKEN
```

## Task Runner

`uv` includes a built-in task runner (like `npm run`):

```toml
# pyproject.toml
[tool.uv.scripts]
serve = "uvicorn main:app --reload"
test = "pytest {args}"
lint = "ruff check . && ruff format --check ."
migrate = "alembic upgrade head"
dev = ["serve", "test"]
```

```bash
uv run serve
uv run test -- tests/test_api.py
uv run lint
```

## Migration from pip/poetry

```bash
# From requirements.txt
uv pip compile requirements.in -o requirements.txt  # generate lock file
uv pip sync requirements.txt                         # install exactly

# From poetry
uv init                      # create pyproject.toml
uv add <each-dependency>     # add from poetry.lock
```

## Common Bugs

- **Missing `requires-python`**: Without it, uv may resolve packages for incompatible Python versions. Always pin `requires-python = ">=3.11"`.
- **Forgetting to commit `uv.lock`**: The lock file ensures reproducibility. Without it, team members and CI get different versions.
- **`uv sync` vs `uv pip install`**: `uv sync` manages the entire environment from `pyproject.toml` + `uv.lock`. `uv pip install` is lower-level and doesn't update the lock file.
- **Platform-specific dependencies**: Some packages (e.g., `uvloop`) don't work on all platforms. Use environment markers: `"uvloop; sys_platform != 'win32'"`.
- **Conflicting tools**: Don't mix `pip install` with `uv add` in the same project. Pick one tool for dependency management.

## Time/Space

- `uv` resolves dependencies ~10–100x faster than `pip` (Rust implementation, parallel downloads).
- Lock file resolution: ~1–5 seconds for 100 dependencies vs ~30–60 seconds with pip-tools.
- Virtual environments: ~20MB base overhead for a standard Python installation.
- `uv sync` with a warm cache: ~50ms for already-installed dependencies.
