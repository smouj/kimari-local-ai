# Support — Kimari Local AI

This document explains where to get help with Kimari Local AI and how to use the right channels for different types of issues.

## Where to Get Help

| Channel | Use For |
|---------|---------|
| [GitHub Issues](https://github.com/smouj/kimari-local-ai/issues) | Bugs, feature requests, performance reports, integration requests |
| [GitHub Discussions](https://github.com/smouj/kimari-local-ai/discussions) | Questions, ideas, show-and-tell, general community conversation |
| [Project Documentation](./docs/) | Installation, configuration, integrations, architecture |

## What Goes in GitHub Issues

Use the [issue tracker](https://github.com/smouj/kimari-local-ai/issues) for:

- **Bug reports** — Something is broken or does not work as documented
- **Feature requests** — New functionality you would like to see
- **Performance reports** — GPU profile issues, VRAM problems, slow inference
- **Integration requests** — Support for new tools, IDEs, or frameworks

When filing an issue, please include:

1. **OS and version** (e.g., Ubuntu 22.04, Windows 11 via WSL2)
2. **GPU model and VRAM** (e.g., GTX 1060 6GB, RTX 3060 12GB)
3. **NVIDIA driver version** (run `nvidia-smi`)
4. **Python version** (run `python --version`)
5. **Kimari version** (run `kimari --version`)
6. **Steps to reproduce**
7. **Expected vs actual behavior**
8. **Relevant log output**

## What Does NOT Go in GitHub Issues

Do **not** use GitHub Issues for:

| Topic | Where to Go |
|-------|-------------|
| **Security vulnerabilities** | See [SECURITY.md](./SECURITY.md) — report privately via email |
| **Code of Conduct violations** | See [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) — report privately |
| **Questions and discussions** | Use [GitHub Discussions](https://github.com/smouj/kimari-local-ai/discussions) |

## Installation Help

- **Linux (native or WSL2):** [docs/INSTALL_WSL2.md](./docs/INSTALL_WSL2.md)
- **Getting started guide:** [GETTING_STARTED.md](./GETTING_STARTED.md)
- **Quick start:** `pip install -e ".[dev]"` then `kimari --help`

## Publishing and Packaging

- **Publishing to PyPI:** [docs/PUBLISHING.md](./docs/PUBLISHING.md)
- **Release checklist:** [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md)

## Integrations

Kimari integrates with several tools. See the integration guides:

- [OpenClaw](./docs/integrations/OPENCLAW.md)
- [Hermes Agent](./docs/integrations/HERMES.md)
- [Continue.dev](./docs/integrations/CONTINUE.md)
- [OpenAI-Compatible Clients](./docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md)

Configuration examples are in [config/integrations/](./config/integrations/).

## Running Diagnostics

Kimari includes built-in diagnostic tools to help troubleshoot issues:

```bash
# Run full environment diagnostics
kimari doctor

# Get detailed system info as JSON
kimari info --json

# Check your configuration
kimari config validate

# Verify a profile works
kimari start --dry-run
```

Include the output of `kimari doctor` or `kimari info --json` in bug reports when possible — it helps reproduce and diagnose issues faster.

## Commercial Support

Kimari Local AI is in **alpha** (v0.1.x-alpha). There is **no guaranteed commercial support** during the alpha phase. Support is provided on a best-effort basis by the maintainer and community through the channels listed above.

As the project matures toward v1.0, support options may expand.
