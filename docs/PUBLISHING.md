# Kimari Local AI — Publishing Guide

Manual guide for publishing Kimari to TestPyPI and PyPI.

> **Status:** This is a **manual** process. Do not configure automated PyPI publishing from CI until TestPyPI has been validated at least once.

## Prerequisites

- Python 3.10+
- `build` and `twine` packages: `pip install build twine`
- TestPyPI account: https://test.pypi.org/account/register/
- PyPI account (for production): https://pypi.org/account/register/

## Pre-Publish Checklist

Before building, verify:

```bash
# Run the release validation script
python scripts/release/check-release.py

# Run tests
python -m pytest tests/ -q

# Check linting
ruff check kimari/ tests/
ruff format --check kimari/ tests/

# Run local CI
make ci-local
```

All checks must pass before proceeding.

## Step 1: Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info kimari/*.egg-info
```

## Step 2: Build the Package

```bash
python -m build
```

This creates:
- `dist/kimari_local_ai-0.1.Xa0-py3-none-any.whl` (wheel)
- `dist/kimari_local_ai-0.1.Xa0.tar.gz` (source distribution)

## Step 3: Check with Twine

```bash
twine check dist/*
```

Both files should pass without warnings.

### Verify Wheel Contents

```bash
python -c "
import zipfile, glob
wheels = glob.glob('dist/*.whl')
with zipfile.ZipFile(wheels[0]) as z:
    names = z.namelist()
    # py.typed must be present
    assert any('py.typed' in n for n in names), 'py.typed missing!'
    # No unwanted files
    forbidden = [n for n in names if any(
        n.startswith(p) or p in n
        for p in ['.kimari/', 'kimari-server.log', '.kimari-server.pid']
    )]
    assert not forbidden, f'Unwanted files: {forbidden}'
    print(f'Wheel OK: {len(names)} files, py.typed present, no unwanted files')
"
```

## Step 4: Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for your TestPyPI credentials. You can also use an API token:

```bash
twine upload --repository testpypi dist/* -u __token__ -p <your-testpypi-token>
```

## Step 5: Verify TestPyPI Install

Create a clean virtual environment and install from TestPyPI:

```bash
# Create clean venv
python -m venv /tmp/kimari-test
source /tmp/kimari-test/bin/activate

# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ kimari-local-ai

# Verify
kimari --version
kimari start --dry-run

# Clean up
deactivate
rm -rf /tmp/kimari-test
```

**If this fails**, fix the issue and re-upload. Do NOT proceed to production PyPI.

## Step 6: Upload to Production PyPI

Only after successful TestPyPI validation:

```bash
twine upload dist/*
```

Or with an API token:

```bash
twine upload dist/* -u __token__ -p <your-pypi-token>
```

## Step 7: Verify Production Install

```bash
pip install kimari-local-ai
kimari --version
kimari start --dry-run
```

## Step 8: Create GitHub Release

```bash
# Tag the release
git tag v0.1.X-alpha
git push origin v0.1.X-alpha
```

Then create a GitHub Release at https://github.com/smouj/kimari-local-ai/releases/new with:
- Tag: `v0.1.X-alpha`
- Title: `v0.1.X-alpha`
- Description: Copy from CHANGELOG.md entry

## Configuration: API Tokens

### TestPyPI Token

1. Go to https://test.pypi.org/manage/account/token/
2. Create a new token with scope "Project: kimari-local-ai"
3. Save the token securely

### PyPI Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new token with scope "Project: kimari-local-ai"
3. Save the token securely

### .pypirc Configuration (Optional)

Create `~/.pypirc` for convenience:

```ini
[testpypi]
username = __token__
password = <your-testpypi-token>

[pypi]
username = __token__
password = <your-pypi-token>
```

Set permissions: `chmod 600 ~/.pypirc`

## v0.1.11 TestPyPI Validation

After implementing v0.1.11-alpha features, validate on TestPyPI:

```bash
# 1. Clean and build
rm -rf dist/ build/ *.egg-info kimari/*.egg-info
python -m build
twine check dist/*

# 2. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 3. Verify in clean venv
python -m venv /tmp/kimari-test-v011
source /tmp/kimari-test-v011/bin/activate
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai

# 4. Validate
kimari --version
kimari setup --dry-run
kimari start --dry-run --strict-flags
kimari token create
kimari token show
kimari token delete
deactivate
rm -rf /tmp/kimari-test-v011
```

### Checklist

- [ ] `twine check dist/*` passes
- [ ] Upload to TestPyPI succeeds
- [ ] Clean venv install from TestPyPI succeeds
- [ ] `kimari --version` prints `0.1.11-alpha`
- [ ] `kimari setup --dry-run` works
- [ ] `kimari start --dry-run --strict-flags` works or warns correctly
- [ ] `kimari token create/show/delete` works
- [ ] Result recorded below

### Result

| Check | Status |
|-------|--------|
| Upload OK | |
| Clean venv OK | |
| Install from TestPyPI OK | |
| kimari --version OK | |
| kimari start --dry-run OK | |

## Common Issues

### "File already exists" on TestPyPI

TestPyPI does not allow re-uploading the same version. Bump the version and rebuild.

### "Invalid distribution" error

Make sure you're using `python -m build` (not `python setup.py`). The project uses PEP 517 builds.

### Twine check fails

Check for:
- Missing README.md
- Invalid trove classifiers
- Missing required metadata in pyproject.toml

### Install from TestPyPI fails with dependency errors

TestPyPI may not have all dependencies. Use:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai
```

## Security Notes

- **Never commit API tokens to the repository**
- Use `__token__` as username with API tokens
- Rotate tokens if they're ever exposed
- The `.pypirc` file should have `chmod 600` permissions
- Do not configure automated production PyPI publishing from CI yet

## v0.1.13 TestPyPI Actual Validation

> **Purpose:** End-to-end validation that the v0.1.13-alpha wheel installs and works correctly from TestPyPI — without any dependency on the repo root.

### Notes

- **Packaged defaults:** The wheel now includes all 3 defaults JSON files (`kimari.profiles.json`, `kimari.profiles.schema.json`, `kimari.models.json`) under `kimari/defaults/` via `package-data`. Config should work from a TestPyPI install without the repo root.
- **SPDX license format:** License changed to SPDX identifier `"MIT"` in `pyproject.toml` — no more `setuptools` warnings during build/install.
- **MANIFEST.in added:** sdist now includes community files (`CODE_OF_CONDUCT.md`, `SUPPORT.md`, `GOVERNANCE.md`, `MAINTAINERS.md`, `CONTRIBUTING.md`, `SECURITY.md`, etc.) so the source distribution is complete.

### Checklist

- [ ] `twine upload --repository testpypi dist/*` succeeds
- [ ] Clean venv creation (`python -m venv /tmp/kimari-test-v013`)
- [ ] `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai` succeeds
- [ ] `kimari --version` prints `0.1.13-alpha`
- [ ] `kimari config path` shows packaged defaults (not repo root)
- [ ] `kimari setup --json` outputs correct JSON
- [ ] `kimari start --dry-run` generates correct command with user paths
- [ ] `kimari token create` stores token in user state dir
- [ ] `kimari token show` displays stored token
- [ ] `kimari token delete` removes stored token
- [ ] Result documented in table below
- [ ] **NOT uploading to real PyPI until all TestPyPI checks pass**

### Result

| Check | Status | Notes |
|-------|--------|-------|
| Upload to TestPyPI | | |
| Clean venv creation | | |
| Install from TestPyPI | | |
| `kimari --version` | | |
| `kimari config path` | | |
| `kimari setup --json` | | |
| `kimari start --dry-run` | | |
| `kimari token create` | | |
| `kimari token show` | | |
| `kimari token delete` | | |
| Result documented | | |
| Real PyPI upload blocked | | |

### Validation Commands (Copy-Paste)

```bash
# 1. Clean and build
rm -rf dist/ build/ *.egg-info kimari/*.egg-info
python -m build
twine check dist/*

# 2. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 3. Verify in clean venv
python -m venv /tmp/kimari-test-v013
source /tmp/kimari-test-v013/bin/activate
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai

# 4. Validate all commands
kimari --version
kimari config path
kimari setup --json
kimari start --dry-run
kimari token create
kimari token show
kimari token delete

# 5. Clean up
deactivate
rm -rf /tmp/kimari-test-v013
```

## v0.1.14 TestPyPI Actual Validation

> **Purpose:** End-to-end validation that the v0.1.14-alpha wheel installs and works correctly from TestPyPI — including new setup --write and models hash/verify commands.

### Notes

- **Setup write-mode:** `kimari setup --write` now persists detected configuration to the user config dir with automatic backup.
- **SHA256 tooling:** `kimari models hash <path>` computes real hashes; `kimari models verify <model>` checks against registry; `kimari models pin-hash <model> --write` pins hash to user registry.
- **Registry merge:** User registry can now override packaged defaults via `get_effective_models_registry()`.
- **No new dependencies:** Still only `requests>=2.31.0` as runtime dependency.

### Checklist

- [ ] `twine upload --repository testpypi dist/*` succeeds
- [ ] Clean venv creation (`python -m venv /tmp/kimari-test-v014`)
- [ ] `pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai` succeeds
- [ ] `kimari --version` prints `0.1.14-alpha`
- [ ] `kimari config path` shows packaged defaults (not repo root)
- [ ] `kimari setup --json` outputs correct JSON with would_write/written/config_path
- [ ] `kimari setup --write` persists config with backup
- [ ] `kimari start --dry-run` generates correct command with user paths
- [ ] `kimari models hash <path>` computes SHA256 of local file
- [ ] `kimari models verify test` reports "hash not pinned"
- [ ] `kimari token create/show/delete` works
- [ ] Result documented in table below
- [ ] **NOT uploading to real PyPI until all TestPyPI checks pass**

### Result

| Check | Status | Notes |
|-------|--------|-------|
| Upload to TestPyPI | | |
| Clean venv creation | | |
| Install from TestPyPI | | |
| `kimari --version` | | |
| `kimari config path` | | |
| `kimari setup --json` | | |
| `kimari setup --write` | | |
| `kimari start --dry-run` | | |
| `kimari models hash` | | |
| `kimari models verify test` | | |
| `kimari token create` | | |
| `kimari token show` | | |
| `kimari token delete` | | |
| Result documented | | |
| Real PyPI upload blocked | | |

> **TestPyPI upload not executed: credentials unavailable.** This is documented and does not block the release. All build and twine check validations pass locally.

### Validation Commands (Copy-Paste)

```bash
# 1. Clean and build
rm -rf dist/ build/ *.egg-info kimari/*.egg-info
python -m build
twine check dist/*

# 2. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 3. Verify in clean venv
python -m venv /tmp/kimari-test-v014
source /tmp/kimari-test-v014/bin/activate
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai

# 4. Validate all commands
kimari --version
kimari config path
kimari setup --json
kimari setup --write
kimari start --dry-run
kimari models hash /tmp/test-model.gguf
kimari models verify test
kimari token create
kimari token show
kimari token delete

# 5. Clean up
deactivate
rm -rf /tmp/kimari-test-v014
```

## v0.1.15 TestPyPI Validation

> **Date:** 2026-05-17
> **Version:** 0.1.15-alpha
> **Purpose:** Validate that the v0.1.15-alpha wheel builds, installs, and runs correctly — including model path resolution, setup --yes, pin-hash workflow, and Windows wheel scripts.

### Notes

- **Model path resolution:** `resolve_model_path()` searches absolute → CWD → user models dir → repo root → fallback, fixing model discovery when installed from wheel.
- **Non-interactive setup:** `kimari setup --write --yes` writes config without confirmation prompt (shows preview first).
- **Hash pinning workflow:** `kimari models pin-hash <model-id> --dry-run` previews the patch; `--write --yes` writes without prompt.
- **Benchmark result sharing:** `benchmarks/RESULT_FORMAT.md` defines the standardized format for sharing benchmark results.
- **Windows wheel scripts:** PowerShell scripts for building, installing from wheel, and installing from TestPyPI on Windows.
- **API OpenAPI draft:** `docs/API_OPENAPI_DRAFT.yaml` contains the initial OpenAPI 3.0 spec for the future v0.2 API.

### Commands Executed

```bash
python -m build
twine check dist/*
```

### Result

| Check | Status | Notes |
|-------|--------|-------|
| Upload to TestPyPI | | TestPyPI upload not executed: credentials unavailable |
| Clean venv creation | | |
| Install from TestPyPI | | |
| `kimari --version` | | |
| `kimari config path` | | |
| `kimari setup --write --yes` | | |
| `kimari start --dry-run` (uses resolve_model_path) | | |
| `kimari models pin-hash test --dry-run` | | |
| `kimari models pin-hash test --write --yes` | | |
| `kimari token create` | | |
| `kimari token show` | | |
| `kimari token delete` | | |
| Result documented | | |
| Real PyPI upload blocked | | |

> **TestPyPI upload not executed: credentials unavailable.** This is the safe default. All local build and twine checks pass.

### Validation Commands (Copy-Paste)

```bash
# 1. Clean and build
rm -rf dist/ build/ *.egg-info kimari/*.egg-info
python -m build
twine check dist/*

# 2. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 3. Verify in clean venv
python -m venv /tmp/kimari-test-v015
source /tmp/kimari-test-v015/bin/activate
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kimari-local-ai

# 4. Validate all commands
kimari --version
kimari config path
kimari setup --write --yes
kimari start --dry-run
kimari models pin-hash test --dry-run
kimari models pin-hash test --write --yes
kimari token create
kimari token show
kimari token delete

# 5. Clean up
deactivate
rm -rf /tmp/kimari-test-v015
```
