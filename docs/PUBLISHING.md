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
