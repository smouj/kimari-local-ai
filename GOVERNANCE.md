# Governance — Kimari Local AI

This document describes how the Kimari Local AI project is governed, how decisions are made, and how releases are produced.

## Project Maintainer

Kimari Local AI is maintained by **Smouj** ([@smouj](https://github.com/smouj)).

The maintainer has final authority over all technical decisions, project direction, and release management.

## Decision Making

### Technical Decisions

Technical decisions are made by the maintainer. This includes:

- Architecture and design choices
- Dependency additions or removals
- CLI interface changes
- Configuration format changes
- Breaking changes

### Community Input

Community input is welcomed and encouraged through:

- [GitHub Issues](https://github.com/smouj/kimari-local-ai/issues) — Feature requests, bug reports, integration requests
- [GitHub Discussions](https://github.com/smouj/kimari-local-ai/discussions) — Ideas, questions, design proposals

While community input is valued, the maintainer makes the final call on all decisions.

## Contributions

Contributions are always welcome via pull requests. All PRs are reviewed by the maintainer.

### Acceptance Criteria

A pull request will be merged only when all of the following are satisfied:

| Criterion | Details |
|-----------|---------|
| **Tests pass** | `python -m pytest tests/ -q` passes with no failures |
| **Ruff clean** | `ruff check kimari/ tests/` and `ruff format --check kimari/ tests/` pass |
| **Docs updated** | CHANGELOG.md, ROADMAP.md, and relevant docs reflect the change |
| **No false claims** | Do not claim features that do not exist (e.g., Kimari-4B is not published) |
| **No security issues** | No hardcoded secrets, no unsafe `0.0.0.0` changes, no token leaks |
| **No GGUF in commits** | Model binary files must not be committed to the repository |
| **No secrets in code** | API keys, tokens, and credentials must not appear in source code |

### Priority

Security and conduct issues take priority over all other work. If a security vulnerability or conduct violation is reported, the maintainer will address it before reviewing other contributions.

## Versioning

Kimari Local AI follows [Semantic Versioning](https://semver.org/) with an `-alpha` suffix during the pre-release phase:

- **Format:** `0.1.X-alpha` (e.g., `0.1.13-alpha`)
- **Major `0`** — The project is in pre-release; the API is not yet stable
- **Minor `1.X`** — New features, changes, and improvements
- **`-alpha` suffix** — Indicates alpha quality; no stability guarantees

Breaking changes may occur between alpha versions. Once the project reaches `v1.0.0`, full semver guarantees will apply.

### No Roadmap Promises During Alpha

Items on the roadmap are **planned, not promised**. During the alpha phase, priorities may shift, features may be delayed, and plans may change. The roadmap represents intent, not commitment.

## Release Process

Releases follow this process:

1. **Version bump** — Update `kimari/__init__.py` and `pyproject.toml`
2. **Run release validation:**
   ```bash
   python scripts/release/check-release.py
   ```
   This checks version consistency, CHANGELOG entries, default profile, no GGUF tracked, no false claims, and more.
3. **Run the full CI suite locally:**
   ```bash
   make ci-local
   ```
4. **Update documentation** — CHANGELOG.md, ROADMAP.md, README.md badge, docs/index.html
5. **Build the package:**
   ```bash
   python -m build
   ```
6. **Validate the package:**
   ```bash
   twine check dist/*
   ```
7. **Publish** (see [docs/PUBLISHING.md](./docs/PUBLISHING.md)):
   ```bash
   twine upload dist/* --repository testpypi  # TestPyPI first
   twine upload dist/*                        # PyPI after verification
   ```
8. **Tag the release:**
   ```bash
   git tag v0.1.X-alpha
   git push origin v0.1.X-alpha
   ```

See [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md) for the full checklist.

## Community Health

The project is committed to maintaining a healthy, inclusive community:

- [Code of Conduct](./CODE_OF_CONDUCT.md) — Enforced for all community spaces
- [Security Policy](./SECURITY.md) — Responsible disclosure process
- [Support](./SUPPORT.md) — Where to get help
- [Contributing Guide](./CONTRIBUTING.md) — How to contribute
