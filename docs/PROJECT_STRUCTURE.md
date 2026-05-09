# Kimari Local AI — Project Structure

> Last updated: v0.1.3-alpha

This document describes the organization of the Kimari Local AI codebase.

## Directory Layout

```
kimari-local-ai/
├── kimari/                    # Main Python package (pip installable)
│   ├── __init__.py           # Package version and metadata
│   ├── cli/                  # CLI interface
│   │   ├── __init__.py
│   │   └── main.py           # argparse CLI, all command handlers
│   ├── core/                 # Core runtime logic
│   │   ├── __init__.py
│   │   ├── constants.py      # Paths, version, ASCII art
│   │   ├── state.py          # Server state management (.kimari/state.json)
│   │   ├── errors.py         # Log error pattern detection
│   │   └── detection.py      # GPU, CUDA, llama-server detection
│   ├── config/               # Configuration management
│   │   ├── __init__.py
│   │   └── loader.py         # Load/validate/migrate config
│   ├── models/               # Model registry and downloads
│   │   ├── __init__.py
│   │   └── registry.py       # Model registry, pull, hash verification
│   ├── profiles/             # GPU profile management
│   │   ├── __init__.py
│   │   └── manager.py        # Profile listing and display
│   ├── benchmarks/           # Benchmarking and KimariFit
│   │   ├── __init__.py
│   │   ├── bench.py          # Benchmark runner
│   │   └── kimarifit.py      # KimariFit score calculation
│   └── utils/                # Shared utilities
│       ├── __init__.py
│       └── colors.py         # Terminal color helpers
│
├── config/                    # External configuration files
│   ├── kimari.profiles.json  # GPU profiles and server settings
│   ├── kimari.profiles.schema.json  # JSON Schema for profiles
│   └── kimari.models.json    # Model registry (download URLs, hashes)
│
├── cli/                       # Legacy CLI entry point
│   ├── kimari_cli.py         # Backward-compatible wrapper → kimari.cli.main
│   └── requirements.txt      # Python dependencies (requests)
│
├── tests/                     # Pytest test suite
│   ├── conftest.py           # Shared fixtures
│   ├── test_cli_smoke.py     # CLI subprocess smoke tests
│   ├── test_config.py        # Config loading and validation
│   ├── test_detection.py     # System detection functions
│   ├── test_error_parsing.py # Log error pattern detection
│   ├── test_kimarifit.py     # KimariFit quality factor
│   ├── test_profiles.py      # GPU profile management
│   ├── test_pull.py          # Model registry and pull
│   ├── test_server_cmd.py    # Server command construction
│   └── test_state.py         # State management
│
├── scripts/                   # Build and installation scripts
│   ├── linux/                # Linux/WSL scripts
│   │   ├── build-llamacpp-cuda.sh
│   │   ├── check-env.py
│   │   ├── smoke-test.sh
│   │   └── ...
│   └── windows/              # Windows scripts
│
├── docs/                      # Documentation
│   ├── 00-01_product_vision.md
│   ├── 00-02_kimarifit_formula.md
│   ├── COMPARISON.md         # Comparison with alternatives
│   ├── WEB_UI_PLAN.md        # Web UI roadmap
│   └── assets/               # Images and logos
│
├── docker/                    # Docker Compose files
├── benchmarks/                # Benchmark results and templates
├── models/                    # Downloaded GGUF models (gitignored)
├── .github/                   # GitHub Actions, issue templates
├── pyproject.toml             # Package configuration (pip installable)
├── requirements-dev.txt       # Dev dependencies
├── Makefile                   # Development tasks and CI
├── SECURITY.md                # Security policy
├── PRIVACY.md                 # Privacy policy
├── README.md                  # Main documentation
├── GETTING_STARTED.md         # Quick start guide
├── ROADMAP.md                 # Version roadmap
└── CHANGELOG.md               # Change history
```

## Key Modules

| Module | Responsibility |
|--------|---------------|
| `kimari.cli.main` | CLI argument parsing and command dispatch |
| `kimari.core.constants` | All paths, version string, ASCII art |
| `kimari.core.state` | Read/write `.kimari/state.json` |
| `kimari.core.errors` | Parse log files for known error patterns |
| `kimari.core.detection` | Detect GPU, CUDA, llama-server binary |
| `kimari.config.loader` | Load/validate/migrate configuration |
| `kimari.models.registry` | Model registry, downloads, hash verification |
| `kimari.profiles.manager` | Profile listing and display |
| `kimari.benchmarks.bench` | Benchmark runner with structured output |
| `kimari.benchmarks.kimarifit` | VRAM estimation and fit score |

## Installation

```bash
# User install
pip install .

# Development install (editable + dev dependencies)
pip install -e ".[dev]"

# Then use:
kimari --help
kimari doctor
```

## Backward Compatibility

The legacy `cli/kimari_cli.py` is kept as a thin wrapper that imports from `kimari.cli.main`. This means:

- `python cli/kimari_cli.py doctor` still works
- `python -m kimari.cli.main doctor` is the new way
- `kimari doctor` works after `pip install`
