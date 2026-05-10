# Contributing to Kimari Local AI

Thank you for your interest in contributing to Kimari! Created by [Smouj](https://github.com/smouj), this project thrives on community contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Linting and CI](#linting-and-ci)
- [Important Rules](#important-rules)
- [Making Changes](#making-changes)
- [Proposing New GPU Profiles](#proposing-new-gpu-profiles)
- [Proposing Integrations](#proposing-integrations)
- [Documenting Changes](#documenting-changes)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Issues](#reporting-issues)
- [Coding Style](#coding-style)
- [Governance](#governance)

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior privately as described in the Code of Conduct — **do not use public GitHub issues for conduct reports**.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your change
4. **Make** your changes
5. **Test** your changes
6. **Submit** a pull request

## Development Setup

### Prerequisites

- **Python 3.10+** (required)
- A CUDA-capable NVIDIA GPU (optional — for testing GPU features)
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/smouj/kimari-local-ai.git
cd kimari-local-ai

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Verify the CLI is available
kimari --help
```

## Running Tests

```bash
# Run the full test suite (quiet output)
python -m pytest tests/ -q

# Or use Makefile targets
make test     # pytest with verbose output
make smoke    # smoke tests

# Run a specific test file
python -m pytest tests/test_config.py -q

# Run a specific test by name
python -m pytest tests/test_kimarifit.py::test_quality_factor -v
```

## Linting and CI

```bash
# Run ruff lint check
ruff check kimari/ tests/

# Run ruff format check
ruff format --check kimari/ tests/

# Run the full local CI pipeline (lint + format + tests + release check)
make ci-local
```

All PRs must pass `make ci-local` before merging.

## Important Rules

The following rules are **non-negotiable** for all contributions:

| Rule | Why |
|------|-----|
| **No downloading models in tests** | Tests must run offline and fast; CI has no GPU |
| **No running llama-server real in CI** | CI has no GPU; use `--dry-run` or mocking |
| **No inventing benchmarks** | All benchmark data must be real, reproducible, and honest |
| **No claiming Kimari-4B is published** | Kimari-4B does not exist yet; do not add it to the model registry or docs as if it does |
| **No changing default_profile from `"test"`** | The default profile is `"test"` for safe first-run experience |
| **No writing real tokens in commits** | Never commit real API tokens, keys, or credentials |
| **No secrets in code** | Use environment variables or user-level config; never hardcode secrets |
| **No unsafe changes to host `0.0.0.0`** | Default must remain `127.0.0.1`; see [SECURITY.md](./SECURITY.md) |
| **No GGUF files in commits** | Model files are large binary blobs; users download them via `kimari pull` |

## Making Changes

### What to Contribute

- **Bug fixes** — Always welcome
- **Documentation** — Improving docs, adding examples
- **Scripts** — New platform support, utility scripts
- **GPU profiles** — New hardware configurations (see below)
- **Integrations** — New tool integrations (see below)
- **Benchmarks** — Real, reproducible benchmark results

### What Needs Review

- Changes to the CLI interface
- New dependencies
- Breaking changes to configuration format
- Changes to llama-server parameters

## Proposing New GPU Profiles

To add support for a new GPU:

1. **Edit `config/kimari.profiles.json`** — Add the new profile with all required fields:
   - `name`, `gpu`, `vram_gb`, `context_size`, `threads`, `n_gpu_layers`, `model`, `estimated_model_size_gb`
   - Optional: `performance_mode`, `flash_attn`, `parallel`, `mlock`, `no_mmap`

2. **Edit `kimari/defaults/kimari.profiles.json`** — Mirror the change so the packaged defaults stay in sync.

3. **Validate the config:**
   ```bash
   kimari config validate
   ```

4. **Test the profile:**
   ```bash
   kimari start --profile <new-profile> --dry-run
   ```

5. **Document it** — Update `CHANGELOG.md` and `ROADMAP.md`.

## Proposing Integrations

To add a new integration (IDE, agent framework, etc.):

1. **Add documentation** — Create `docs/integrations/<NAME>.md` with:
   - What the integration does
   - Prerequisites
   - Step-by-step setup instructions
   - Configuration example
   - Troubleshooting

2. **Add a config example** — Create `config/integrations/<name>.kimari.example.json` (or `.yaml`).

3. **Test it** — Verify the integration works with `kimari start` and the target tool.

4. **Document it** — Update `CHANGELOG.md` and `ROADMAP.md`.

Existing integrations for reference:
- [OpenClaw](./docs/integrations/OPENCLAW.md) + [config](./config/integrations/openclaw.kimari.example.json)
- [Hermes Agent](./docs/integrations/HERMES.md) + [config](./config/integrations/hermes.kimari.example.yaml)
- [Continue.dev](./docs/integrations/CONTINUE.md) + [config](./config/integrations/continue.kimari.example.yaml)

## Documenting Changes

When making changes that affect users or the project:

- **Update [CHANGELOG.md](./CHANGELOG.md)** — Add your change under the appropriate version heading.
- **Update [ROADMAP.md](./ROADMAP.md)** — If your change affects planned features or milestones.

Follow the existing format in both files. Keep entries concise and honest.

## Submitting a Pull Request

1. **Update tests** if you're changing behavior
2. **Update documentation** if you're adding features
3. **Ensure CI passes** — run `make ci-local` locally before pushing
4. **Write a clear description** — explain what and why
5. **Keep it small** — one logical change per PR

### PR Checklist

- [ ] Code compiles without errors
- [ ] `python -m pytest tests/ -q` passes
- [ ] `ruff check kimari/ tests/` passes
- [ ] `ruff format --check kimari/ tests/` passes
- [ ] `make ci-local` passes
- [ ] Documentation updated (if applicable)
- [ ] No new dependencies without discussion
- [ ] Commit messages are clear and descriptive
- [ ] No real tokens, secrets, or GGUF files in the diff
- [ ] `default_profile` is still `"test"`
- [ ] No false claims (e.g., Kimari-4B is not published)
- [ ] No unsafe changes to `0.0.0.0` binding

## Reporting Issues

When reporting bugs, please include:

1. **OS and version** (e.g., Ubuntu 22.04)
2. **GPU model and VRAM** (e.g., GTX 1060 6GB)
3. **NVIDIA driver version** (run `nvidia-smi`)
4. **Python version** (run `python --version`)
5. **Kimari version** (run `kimari --version`)
6. **Steps to reproduce**
7. **Expected vs actual behavior**
8. **Relevant log output**

Use the [GitHub issue tracker](https://github.com/smouj/kimari-local-ai/issues) with appropriate labels.

For other types of reports, see [SUPPORT.md](./SUPPORT.md):
- **Security vulnerabilities** → [SECURITY.md](./SECURITY.md)
- **Conduct violations** → [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- **Questions** → [GitHub Discussions](https://github.com/smouj/kimari-local-ai/discussions)

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

## Governance

This project is maintained by Smouj (@smouj). See [GOVERNANCE.md](./GOVERNANCE.md) for decision-making processes, acceptance criteria, and release procedures.

---

Thank you for contributing to Kimari!
