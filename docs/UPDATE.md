# Kimari Update Guide

How to check for updates and update your Kimari Local AI installation.

---

## Version Format

Kimari uses semantic versioning with a pre-release suffix:

```
MAJOR.MINOR.PATCH-pre
```

Example: `0.1.26-alpha`

- **MAJOR**: Breaking changes
- **MINOR**: New features
- **PATCH**: Bug fixes
- **Pre-release suffix**: `-alpha`, `-beta`, `-rc` etc.

Check your current version:

```bash
kimari --version
```

---

## Checking for Updates

### Offline Mode (Default)

Checks locally installed version only — no network access required.

```bash
kimari update check
```

Output includes:
- Currently installed version
- Installation method (dev/wheel/pip)
- Recommendation to use `--online` for checking available updates

### Online Mode

Checks GitHub tags and PyPI for newer versions.

```bash
kimari update check --online
```

This queries:
- **GitHub tags**: Checks `https://github.com/smouj/kimari-local-ai/tags` for the latest release tag
- **PyPI availability**: Checks if the latest version is available on PyPI or TestPyPI

### JSON Output

For scripting and automation:

```bash
kimari update check --json
kimari update check --online --json
```

Returns structured JSON with version info, available updates, and installation method.

---

## Updating

There is **no auto-update** yet. You must update manually based on your installation method.

### Dev Install (Editable)

If you installed from the git repository with `pip install -e .`:

```bash
cd /path/to/kimari-local-ai
git pull
pip install -e .
```

If you installed with dev dependencies:

```bash
cd /path/to/kimari-local-ai
git pull
pip install -e ".[dev]"
```

### Wheel Install

If you installed from a `.whl` file:

```bash
# Download or build the new wheel first
pip install --upgrade path/to/dist/kimari_local_ai-*.whl
```

### TestPyPI

If installing from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  kimari-local-ai
```

> **Note**: TestPyPI may lag behind the latest GitHub release. Use `--pre` flag if you need pre-release versions.

### Future: PyPI

When Kimari is published to PyPI:

```bash
pip install --upgrade kimari-local-ai
```

> **Note**: Kimari is not yet published on PyPI. This command will not work until the first public release.

---

## Before Updating

### Backup Your Configuration

Always back up your configuration before any update:

```bash
cp ~/.config/kimari/kimari.json ~/.config/kimari/kimari.json.bak
```

Or if using the profiles config:

```bash
cp ~/.config/kimari/kimari.profiles.json ~/.config/kimari/kimari.profiles.json.bak
```

### Check for Breaking Changes

Review the changelog before updating:

```bash
# View the changelog
kimari info
```

Or read [CHANGELOG.md](../CHANGELOG.md) directly on GitHub.

### Verify After Update

After updating, verify your installation:

```bash
kimari --version
kimari doctor
```

`kimari doctor` checks:
- Python version
- CUDA availability
- llama-server binary
- Configuration validity
- Model availability
- Port availability

For a deeper check:

```bash
kimari doctor --deep
```

---

## Update Troubleshooting

### Version didn't change after `git pull`

Make sure you re-installed:
```bash
pip install -e .
```

### Wheel install fails

Ensure the wheel matches your Python version and platform:
```bash
python --version
pip debug --verbose
```

### TestPyPI returns old version

TestPyPI may not have the latest build. Check available versions:
```bash
pip index versions kimari-local-ai --index-url https://test.pypi.org/simple/
```

### Config errors after update

Restore your backup:
```bash
cp ~/.config/kimari/kimari.json.bak ~/.config/kimari/kimari.json
```

Then re-run setup if needed:
```bash
kimari setup --write
```

---

## Summary Table

| Method | Check Update | Update Command |
|--------|-------------|----------------|
| Dev install | `git fetch && git log HEAD..origin/main --oneline` | `git pull && pip install -e .` |
| Wheel | `kimari update check --online` | `pip install --upgrade path/to/dist/kimari_local_ai-*.whl` |
| TestPyPI | `kimari update check --online` | `pip install -i https://test.pypi.org/simple/ kimari-local-ai` |
| PyPI (future) | `kimari update check --online` | `pip install --upgrade kimari-local-ai` |

---

*No auto-update mechanism exists yet. All updates must be performed manually.*
