# Deep Doctor Diagnostic — `kimari doctor --deep`

> **Document Type:** User guide
> **Applies to:** Kimari Local AI alpha releases
> **Source module:** `kimari/doctor/deep.py`

---

## Overview

`kimari doctor --deep` runs extended diagnostics beyond the basic `kimari doctor` command. While the basic doctor checks your OS, GPU, driver, CUDA, and llama-server, the deep doctor performs a comprehensive audit of your entire Kimari environment — covering Python version, directory paths, configuration health, model availability, server binary, profile correctness, security tooling, benchmark data, and the adapter preview gate.

All deep checks are **pure and safe** — they perform no model execution, no downloads, no GPU computation, and no network calls. They only inspect local files, directories, and environment state.

---

## What It Checks

The deep doctor runs 9 checks in order:

| # | Check | What It Verifies | PASS Condition | WARN Condition | FAIL Condition |
|---|-------|-------------------|----------------|----------------|----------------|
| 1 | **Python** | Python interpreter version | >= 3.10 | >= 3.8 but < 3.10 | < 3.8 |
| 2 | **Paths** | Key directories exist (kimari home, models dir, state dir, config dir) | All directories exist | Some directories missing | All directories missing |
| 3 | **Config** | Config file exists and is valid JSON | File exists, valid JSON, passes validation | File exists but has validation issues | File missing or corrupt JSON |
| 4 | **Models Dir** | Models directory has GGUF files | GGUF files found | Directory exists but no GGUF files | Directory does not exist |
| 5 | **llama-server** | `llama-server` binary found in PATH or env var | Binary found (path shown) | Binary not found | — |
| 6 | **Default Profile** | `default_profile` is set to `test` during alpha | `default_profile == "test"` | Profile is not `test` or config not loadable | — |
| 7 | **Secret Scanner** | `scripts/security/scan_for_secrets.py` exists | File exists | File not found | — |
| 8 | **Benchmark Prompts** | `benchmarks/prompts/local_benchmark_prompts.jsonl` exists and contains valid JSON lines | File exists with valid JSON lines | File missing, empty, or unreadable | File contains invalid JSON |
| 9 | **Preview Gate** | Adapter preview gate is BLOCKED during alpha | Gate is BLOCKED | — | Unconditional APPROVED claim found in gate document |

### Check Details

**1. Python version** — Kimari requires Python 3.10 or newer. Python 3.8–3.9 may work but are not officially supported. Anything below 3.8 will not work at all.

**2. Key paths** — Four directories are verified:
- **kimari home** — The `.kimari` directory (via `get_kimari_home()`)
- **models dir** — Where GGUF model files are stored (via `get_user_models_dir()`)
- **state dir** — Runtime state directory (via `get_user_state_dir()`)
- **config dir** — Configuration directory (via `get_user_config_dir()`)

**3. Config file** — The config is loaded via `kimari.config.loader.load_config()` and validated via `validate_config()`. Common issues caught include missing fields, invalid host values (`0.0.0.0` on non-docker profiles), absolute model paths, and out-of-range ports.

**4. Models directory** — Recursively scans the models directory for `.gguf` files. At minimum one model must be present to run inference.

**5. llama-server binary** — Uses `kimari.core.detection.detect_llama_server()` which checks the `LLAMA_SERVER` environment variable, `KIMARI_LLAMA_SERVER` environment variable, and the system `PATH`.

**6. Default profile** — During the alpha phase, the default profile must be `"test"`. This ensures the small TinyLlama test model is used rather than a full-size model that may not be available yet.

**7. Secret scanner** — Verifies that `scripts/security/scan_for_secrets.py` is present. This script is used to scan adapter artifacts for leaked secrets before any release.

**8. Benchmark prompts** — Validates `benchmarks/prompts/local_benchmark_prompts.jsonl` exists and that every line is valid JSON. This file provides the prompt set for local benchmarking runs.

**9. Preview gate** — Checks `docs/ADAPTER_PREVIEW_GATE.md` for any unconditional `APPROVED` claims. During alpha, the gate must remain BLOCKED. Conditional state names like `APPROVED_FOR_PRIVATE_TESTING` and `APPROVED_FOR_PUBLIC_PREVIEW` are allowed since they are part of the defined state machine and require explicit human decisions.

---

## How to Interpret PASS/WARN/FAIL

Each check returns one of three statuses:

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **PASS** | Everything is fine for this check. | None — your environment is healthy for this area. |
| **WARN** | Suboptimal but Kimari may work with limitations. | Review the detail message. Fix when convenient. Some features may be degraded or unavailable. |
| **FAIL** | This must be fixed before proceeding. | Stop and resolve the issue. Kimari will not function correctly until this is addressed. |

### Summary Output

After all 9 checks, a summary is printed:

```
Summary: 7 PASS, 2 WARN, 0 FAIL
```

- **0 FAIL** — Your environment is ready. Any WARN items can be addressed later.
- **1+ FAIL** — Fix the failing checks before running benchmarks or private training.
- **Multiple WARN** — Review each one. Some may indicate missing tools that limit functionality.

---

## Usage

### Human-readable output

```bash
kimari doctor --deep
```

This prints a color-coded table showing each check, its status, and any detail messages.

### Machine-readable JSON output

```bash
kimari doctor --deep --json
```

Returns a JSON object with the full list of check results and summary counts. Each check result has four keys:

```json
{
  "name": "Python",
  "status": "PASS",
  "value": "3.12.1",
  "detail": ""
}
```

The summary entry follows the checks:

```json
{
  "name": "Summary",
  "status": "INFO",
  "value": {
    "total": 9,
    "pass_count": 7,
    "warn_count": 2,
    "fail_count": 0
  },
  "detail": ""
}
```

### When to run it

Run `kimari doctor --deep` in these situations:

- **Before running benchmarks** — Verify that models, prompts, and llama-server are all in place.
- **Before private training** — Confirm the environment is fully configured and the preview gate is properly BLOCKED.
- **After installation** — Validate that the initial setup completed correctly.
- **After updating** — Check that nothing broke during an upgrade.
- **When troubleshooting** — Get a comprehensive view of your environment state.

---

## Common WARN/FAIL Resolutions

### Python too old

```
WARN  Python: 3.9.7 — Python >= 3.10 recommended
FAIL  Python: 3.7.3 — Python >= 3.8 required
```

**Fix:** Upgrade Python to 3.10 or newer. Use your system package manager or [pyenv](https://github.com/pyenv/pyenv):

```bash
# Using pyenv
pyenv install 3.12
pyenv global 3.12

# Or on Ubuntu/Debian
sudo apt install python3.12
```

---

### Missing key directories

```
WARN  Paths: Missing: state_dir, config_dir
FAIL  Paths: Missing: kimari_home, models_dir, state_dir, config_dir
```

**Fix:** Run `kimari setup` to create missing directories, or check that the `KIMARI_HOME` environment variable points to the correct location.

---

### Config file issues

```
FAIL  Config: Config not found — Run 'kimari config path' to locate config
FAIL  Config: Invalid JSON — Expecting ',' delimiter: line 12 column 3
WARN  Config: Config has 2 issue(s) — host 0.0.0.0 on non-docker profile; absolute model path
```

**Fix:**
- **Missing config:** Run `kimari config path` to check where it should be. Copy or regenerate the config.
- **Invalid JSON:** Open the config file and fix the syntax error.
- **Validation issues:** Run `kimari config validate` for detailed error messages, then correct the reported problems.

---

### No models available

```
WARN  Models Dir: No GGUF files found — Run 'kimari pull test' to download a model
FAIL  Models Dir: Directory does not exist
```

**Fix:**
- **No GGUF files:** Pull the test model:
  ```bash
  kimari pull test
  ```
- **Directory missing:** Create the models directory or run `kimari setup`:
  ```bash
  mkdir -p models
  kimari pull test
  ```

---

### llama-server not found

```
WARN  llama-server: Not found — Build from source or set LLAMA_SERVER env var
```

**Fix:** There are three options:

1. **Build from source** (recommended):
   ```bash
   # With CUDA
   make build-cuda

   # With AMD ROCm
   make build-rocm
   ```

2. **Set the `LLAMA_SERVER` environment variable** if you have the binary elsewhere:
   ```bash
   export LLAMA_SERVER=/path/to/llama-server
   ```

3. **Install via pip** (if a pre-built wheel is available for your platform):
   ```bash
   pip install llama-cpp-python[server]
   ```

---

### Wrong default profile

```
WARN  Default Profile: gtx1060 — Expected 'test' during alpha
```

**Fix:** Edit your config file and set `default_profile` to `"test"`:

```bash
kimari config show
# Edit the config to set: "default_profile": "test"
kimari config validate
```

This is expected during alpha — the `test` profile uses the small TinyLlama model which is always available.

---

### Secret scanner missing

```
WARN  Secret Scanner: Not found — scripts/security/scan_for_secrets.py missing
```

**Fix:** Verify that `scripts/security/scan_for_secrets.py` exists in your Kimari installation. If it is missing, your repository may be incomplete. Re-clone or restore the file:

```bash
ls scripts/security/scan_for_secrets.py
# If missing, verify your repo is intact:
git status
git checkout scripts/security/scan_for_secrets.py
```

---

### Benchmark prompts missing or invalid

```
WARN  Benchmark Prompts: File not found — benchmarks/prompts/local_benchmark_prompts.jsonl missing
WARN  Benchmark Prompts: File is empty
FAIL  Benchmark Prompts: Invalid JSON on line 3 — Expecting value: line 1 column 1
```

**Fix:**
- **Missing file:** The benchmark prompts file should exist in the repository. Restore it from git:
  ```bash
  git checkout benchmarks/prompts/local_benchmark_prompts.jsonl
  ```
- **Empty file:** The file exists but has no prompts. Check that it was not accidentally truncated.
- **Invalid JSON:** Each line in the JSONL file must be a valid JSON object. Open the file and fix the syntax error on the reported line.

---

### Preview gate not BLOCKED

```
FAIL  Preview Gate: NOT BLOCKED — Unconditional APPROVED found: STATUS: APPROVED
```

**Fix:** During the alpha phase, the adapter preview gate must remain BLOCKED. Review `docs/ADAPTER_PREVIEW_GATE.md` and remove any unconditional `APPROVED` claims. All approvals must be conditional (e.g., `APPROVED_FOR_PRIVATE_TESTING`) and require explicit human decisions per the state machine defined in that document.

---

## Relationship to Other Commands

| Command | Purpose |
|---------|---------|
| `kimari doctor` | Basic diagnostics — OS, GPU, driver, CUDA, llama-server |
| `kimari doctor --deep` | Extended diagnostics — all basic checks plus paths, config, models, profile, security, benchmarks, preview gate |
| `kimari setup` | Guided first-time setup with environment detection |
| `kimari config validate` | Detailed config validation with specific error messages |
| `kimari info` | Quick summary of Kimari version and installation paths |

---

## Implementation Reference

The deep doctor is implemented in `kimari/doctor/deep.py`. The orchestrator function `run_deep_checks()` runs all 9 checks sequentially and appends a summary dict. Each check function is pure — it takes no parameters (resolving paths through `kimari.core.constants` and `kimari.core.paths`) and returns a dict with keys `name`, `status`, `value`, and `detail`.

For testing, monkeypatch `kimari.core.constants.PROJECT_ROOT` or the `kimari.core.paths` functions rather than passing a custom project root.
