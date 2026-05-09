# Contributing to Kimari

Thank you for your interest in contributing to Kimari! This guide explains how to get involved.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Issues](#reporting-issues)
- [Coding Style](#coding-style)

## Code of Conduct

Be respectful, constructive, and inclusive. We welcome contributors of all backgrounds and experience levels.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your change
4. **Make** your changes
5. **Test** your changes
6. **Submit** a pull request

## Development Setup

### Prerequisites

- Python 3.10 or newer
- A CUDA-capable NVIDIA GPU (optional — for testing GPU features)
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/your-username/kimari-local-ai.git
cd kimari-local-ai

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r cli/requirements.txt

# Run diagnostics
make doctor
```

### Running Tests

```bash
# Smoke tests
make smoke

# Run specific tests
bash scripts/linux/healthcheck.sh
bash scripts/linux/chat-test.sh
```

## Making Changes

### What to Contribute

- **Bug fixes** — Always welcome
- **Documentation** — Improving docs, adding examples
- **Scripts** — New platform support, utility scripts
- **Profiles** — GPU configurations for new hardware
- **Benchmarks** — New test prompts, evaluation criteria
- **Skills** — New skill definitions for model evaluation

### What Needs Review

- Changes to the CLI interface
- New dependencies
- Breaking changes to configuration format
- Changes to llama-server parameters

## Submitting a Pull Request

1. **Update tests** if you're changing behavior
2. **Update documentation** if you're adding features
3. **Ensure CI passes** — our CI checks Python syntax, bash scripts, and JSON configs
4. **Write a clear description** — explain what and why
5. **Keep it small** — one logical change per PR

### PR Checklist

- [ ] Code compiles without errors
- [ ] `make smoke` passes
- [ ] Documentation updated (if applicable)
- [ ] No new dependencies without discussion
- [ ] Commit messages are clear and descriptive

## Reporting Issues

When reporting bugs, please include:

1. **OS and version** (e.g., Ubuntu 22.04)
2. **GPU model and VRAM** (e.g., GTX 1060 6GB)
3. **NVIDIA driver version** (run `nvidia-smi`)
4. **Python version** (run `python --version`)
5. **Steps to reproduce**
6. **Expected vs actual behavior**
7. **Relevant log output**

Use the GitHub issue tracker with appropriate labels.

## Coding Style

### Python

- Follow PEP 8
- Use type hints where practical
- Maximum line length: 100 characters
- Docstrings for public functions
- Use f-strings for formatting

### Bash

- Use `set -euo pipefail` in all scripts
- Quote all variable expansions
- Use `#!/usr/bin/env bash` shebang
- Validate inputs before use

### JSON

- Use 2-space indentation
- Keep files valid — validate before committing
- No trailing commas

### General

- Write self-documenting code
- Add comments for non-obvious logic
- Keep functions focused and small
- Handle errors gracefully

## Community

- **Discussions** — Use GitHub Discussions for questions
- **Issues** — Use GitHub Issues for bugs and feature requests
- **PRs** — Use Pull Requests for code changes

Thank you for contributing to Kimari! 🎉
