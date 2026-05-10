# Release Checklist

Use this checklist before publishing any Kimari Local AI release.

## Version & Metadata

- [ ] Version bumped in `pyproject.toml`
- [ ] Version bumped in `kimari/__init__.py` (`__version__`)
- [ ] README.md version badge updated
- [ ] `docs/index.html` version references updated

## Changelog & Roadmap

- [ ] `CHANGELOG.md` entry added for the new version (Keep a Changelog format)
- [ ] `ROADMAP.md` updated — previous version marked "Released", new version marked "Current"

## Testing

- [ ] `python -m pytest tests/ -q` — all tests pass
- [ ] `ruff check kimari/ tests/` — zero lint errors
- [ ] `ruff format --check kimari/ tests/` — zero format errors
- [ ] `make ci-local` — full local CI passes

## CLI Validation

- [ ] `python -m kimari.cli.main --version` — prints correct version
- [ ] `python -m kimari.cli.main start --dry-run` — works without `--profile`
- [ ] `pip install -e .` — installs without errors
- [ ] `kimari --version` — installed entry point works
- [ ] `kimari start --dry-run` — installed entry point works
- [ ] `kimari optimize --profile test --json` — returns valid JSON
- [ ] `kimari perf --profile test --dry-run` — runs without error

## Build & Package

- [ ] `python -m build` — builds without errors
- [ ] `twine check dist/*` — no warnings or errors
- [ ] Wheel contains `kimari/py.typed`
- [ ] Wheel does **not** contain `models/*.gguf`, `.kimari/`, `kimari-server.log`, or `.kimari-server.pid`

## Release Validation Script

- [ ] `python scripts/release/check-release.py` — all checks pass

## Content Review

- [ ] Kimari-4B is **not** advertised as published/released
- [ ] ROCm is marked as **experimental** (not stable)
- [ ] SHA256 verification is **not** marked as enforced if hashes are still `null`
- [ ] `default_profile` is `"test"` in `config/kimari.profiles.json`
- [ ] No GGUF files are tracked in git
- [ ] GitHub Pages (`docs/index.html`) checked locally or via file review
- [ ] `docs/index.html` SEO metadata is present (canonical, og:title, og:image)
- [ ] `docs/INSTALL_WSL2.md` is up to date
- [ ] `docs/PUBLISHING.md` is up to date
- [ ] README links to Release Checklist
- [ ] ROADMAP marks current version as "Current"
- [ ] No "Kimari-4B released" false claim anywhere
- [ ] docs/integrations/OPENCLAW.md exists and mentions Chat Completions (not Responses API)
- [ ] docs/integrations/HERMES.md exists
- [ ] docs/integrations/CONTINUE.md exists
- [ ] docs/integrations/OPENAI_COMPATIBLE_CLIENTS.md exists
- [ ] config/integrations/ directory with example configs exists
- [ ] No "Responses API supported" false claim anywhere
- [ ] New profiles exist (gtx1060-safe, gtx1060-fast, gtx1080-balanced, gtx1080-longctx, ide-local, agent-local, openclaw-local, hermes-local)

## Publishing (Manual)

### TestPyPI (Pre-release Validation)

Before publishing to the real PyPI, validate the package on TestPyPI:

```bash
# 1. Build the package
python -m build

# 2. Check with twine
twine check dist/*

# 3. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 4. Verify the package installs correctly from TestPyPI
pip install -i https://test.pypi.org/simple/ kimari-local-ai
```

> **Note:** This is manual for now. Do not configure automated PyPI publishing from CI until TestPyPI has been validated at least once.

### PyPI (Production)

Do **not** upload to the real PyPI until TestPyPI validation passes and the version is confirmed working:

```bash
# Only after successful TestPyPI validation
twine upload dist/*
```

### GitHub Release

- [ ] GitHub Release created with notes from CHANGELOG
- [ ] Git tag created: `git tag v0.1.X-alpha && git push origin v0.1.X-alpha`

## Post-Release

- [ ] GitHub topics still accurate (20 topics, lowercase, hyphens)
- [ ] `docs/index.html` live site reflects new version
- [ ] ROADMAP.md next version entry created
- [ ] TestPyPI validation result recorded (if attempted)
- [ ] GitHub release tag pushed
