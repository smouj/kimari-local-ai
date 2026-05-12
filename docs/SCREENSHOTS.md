# Screenshots & CLI Preview

This document provides a gallery of Kimari Local AI screenshots and CLI output examples.

> **Important:** All screenshots are **illustrative**. They show CLI output structure, not real training outputs or benchmark results.
>
> - **No secrets** — API keys, tokens, or private paths are never shown.
> - **No real training outputs** — Adapter weights, loss curves, and raw eval outputs are local-only.
> - **No real benchmarks** — No benchmark claims are made until measured and reviewed.
> - **Kimari-4B is not released** — No weights, adapters, or GGUF files are available yet.

---

## CLI Screenshots

### `kimari setup --json`

Detects your environment (GPU, CUDA, llama-server, models) and recommends configuration.

```json
{
  "profile": "test",
  "gpu_detected": true,
  "cuda_available": true,
  "recommended_profile": "gtx1060",
  "llama_server_found": true,
  "models_dir": "/home/user/.local/share/kimari/models",
  "config_path": "/home/user/.config/kimari/config.json"
}
```

### `kimari optimize --profile test --json`

Analyzes your GPU profile and recommends optimal settings.

```json
{
  "profile": "test",
  "mode": "balanced",
  "vram_estimated_gb": 5.8,
  "context_window": 4096,
  "cache_type_k": "q8_0",
  "cache_type_v": "q8_0",
  "batch_size": 512,
  "ubatch_size": 128
}
```

### `kimari status`

Shows the current server status — running state, profile, model, host, port, and uptime.

```
Kimari CLI v0.1.27-alpha

  Status:      READY
  Profile:     test
  Model:       tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
  Host:        127.0.0.1
  Port:        11435
  PID:         12345
  Uptime:      5m 32s
  Gateway:     planned
```

### `kimari doctor --deep`

Runs 14 extended diagnostic checks with PASS/WARN/FAIL status.

```
Kimari CLI v0.1.27-alpha — Deep Doctor

  #   Check              Status   Detail
  --  -----------------  -------  ------------------------------
  1   Python             PASS     3.12.1
  2   Paths              PASS     All directories exist
  3   Config             PASS     Configuration is valid
  4   Models Dir         PASS     2 GGUF files found
  5   llama-server       PASS     /usr/local/bin/llama-server
  6   Default Profile    PASS     test
  7   Secret Scanner     PASS     Found
  8   Benchmark Prompts  PASS     7 valid prompts
  9   Preview Gate       PASS     BLOCKED
  10  Kimari Version     PASS     0.1.27-alpha
  11  CUDA/NVIDIA        WARN     No GPU detected
  12  Packaged Defaults  PASS     All defaults found
  13  Gateway Module     PASS     Module exists
  14  Integration Docs   PASS     All docs found

Summary: 12 PASS, 2 WARN, 0 FAIL
```

### `kimari gateway --plan`

Shows the planned gateway endpoint map and security constraints.

```
Kimari Gateway Plan

  Endpoints:
    GET    /health                   — Health check
    GET    /status                   — Server status
    GET    /profiles                 — Available profiles
    GET    /models                   — Available models
    GET    /config                   — Current configuration
    GET    /logs                     — Recent log entries
    GET    /integrations             — Integration status
    POST   /server/start             — Start llama-server
    POST   /server/stop              — Stop llama-server
    POST   /benchmark/run            — Run benchmark

  Security:
    default_host             : 127.0.0.1
    default_port             : 11436
    bind_localhost_only      : True
    no_public_exposure       : True
    no_token_storage         : True
    no_model_upload          : True
    no_training_execution    : True
    no_hf_publishing         : True

  No server is started. This is a plan only.
```

### `kimari integrations generate --all`

Generates configuration snippets for all supported integration targets (Open WebUI, OpenClaw, Hermes, Continue.dev). No tokens, no API keys, no auto-writing.

```json
{
  "openwebui": {
    "type": "openai",
    "baseUrl": "http://127.0.0.1:11435/v1",
    "apiKey": "kimari-local",
    "modelName": "kimari"
  },
  "openclaw": {
    "baseUrl": "http://127.0.0.1:11435/v1",
    "apiKey": "kimari-local",
    "api": "openai-completions",
    "timeoutSeconds": 300,
    "model": "kimari"
  },
  "hermes": {
    "endpoint": "http://127.0.0.1:11435/v1",
    "apiKey": "kimari-local",
    "apiType": "openai-chat-completions",
    "timeoutSeconds": 300,
    "model": "kimari"
  },
  "continue": {
    "models": [
      {
        "title": "Kimari Local",
        "provider": "openai",
        "model": "kimari",
        "apiBase": "http://127.0.0.1:11435/v1",
        "apiKey": "kimari-local"
      }
    ]
  }
}
```

### `kimari benchmark --dry-run`

Shows what a benchmark would measure without actually executing it.

```json
{
  "mode": "dry-run",
  "profile": "test",
  "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
  "prompts_count": 7,
  "estimated_duration_s": 120,
  "categories": ["coding_python", "coding_typescript", "json_mode", "agent_prompting", "spanish_technical", "server_debugging", "long_context"],
  "dry_run": true
}
```

### `kimari update check`

Checks for Kimari updates. Offline by default; use `--online` to check GitHub.

```
Kimari Update Check

  Current version:   0.1.27-alpha
  Latest GitHub tag: (not checked — use --online)
  PyPI available:    N/A
  Update available:  N/A
  Auto-update:       False

  No update check performed. Use --online to check GitHub.
  Use --online to check GitHub for the latest release.
```

### `preflight_private_sft.py --json`

Checks SFT readiness before training. Works without torch installed (graceful degradation).

```json
{
  "checks": {
    "python_version": { "status": "PASS", "value": "3.12.3" },
    "torch": { "status": "WARN", "value": "missing", "message": "torch is not installed" },
    "dataset_build": { "status": "WARN", "value": "...", "exists": false, "source": "fallback" },
    "preview_gate": { "status": "PASS", "value": "BLOCKED" }
  },
  "overall": "warn",
  "dataset_build_dir_source": "fallback"
}
```

### `run_training_command_preview.py --json`

Shows the recommended training command without executing anything.

```json
{
  "recommended_command": "accelerate launch training/scripts/train_sft_lora.py --config training/configs/kimari_sft_lora.v0.example.yaml",
  "recommended_environment": "RunPod RTX 4090 24GB / Local A100",
  "expected_outputs": ["adapter_model.safetensors", "MANIFEST.yaml"],
  "forbidden_commit_patterns": ["*.safetensors", "*.bin", "*.pt", "*.gguf"],
  "safety_warnings": ["Do not commit adapter weights", "Preview gate must stay BLOCKED"]
}
```

### `run_baseline_eval_plan.py --dry-run --json`

Plans baseline evaluation for SmolLM3-3B before fine-tuning.

```json
{
  "model_label": "smollm3-base",
  "prompt_count": 35,
  "categories": ["python", "bash", "docker", "linux_troubleshooting", "..."],
  "recommended_endpoint": "http://127.0.0.1:11435/v1/chat/completions",
  "score_status": "manual_review_required",
  "dry_run": true
}
```

### `postrun_private_sft.py --dry-run --json`

Orchestrates post-training steps (manifest, eval summary, compare, gate check).

```json
{
  "steps": [
    { "label": "create_adapter_manifest", "status": "dry_run" },
    { "label": "create_eval_summary", "status": "dry_run" },
    { "label": "compare_runs", "status": "skipped" },
    { "label": "verify_gate_blocked", "status": "dry_run", "blocked": true }
  ],
  "overall": "pass",
  "dry_run": true
}
```

---

## GitHub Pages Landing

The project landing page at [smouj.github.io/kimari-local-ai](https://smouj.github.io/kimari-local-ai/) showcases:
- Hero section with version badge
- Quick Start guide
- GPU profiles table
- CLI commands overview
- Integration guides (Open WebUI, Continue, OpenClaw, Hermes)
- Documentation cards
- Honest status section (no false claims)
- CLI Preview section with code cards

---

## Screenshot Policy

See [docs/assets/screenshots/README.md](assets/screenshots/README.md) for:
- Naming conventions
- Allowed formats (PNG/WebP)
- Content guidelines (no secrets, no benchmarks, no fake UI)
- Recommended dimensions
- Alt text requirements

---

## Planned Screenshots

The following screenshots are planned for capture when running in a real GPU environment:

| File | Command | Notes |
|------|---------|-------|
| `kimari-status.png` | `kimari status` | Server status — running state, profile, model |
| `kimari-doctor-deep.png` | `kimari doctor --deep` | Extended diagnostics — PASS/WARN/FAIL table |
| `kimari-gateway-plan.png` | `kimari gateway --plan` | Gateway endpoint plan and security constraints |
| `kimari-integrations-generate.png` | `kimari integrations generate --all` | Integration config snippets (no tokens) |
| `kimari-benchmark-dry-run.png` | `kimari benchmark --dry-run` | Benchmark dry-run plan (no real benchmarks) |
| `kimari-update-check.png` | `kimari update check` | Update check — version info |
| `kimari-setup-json.png` | `kimari setup --json` | Environment detection output |
| `kimari-preflight-private-sft.png` | `preflight_private_sft.py --json` | Preflight check results |
| `kimari-training-command-preview.png` | `run_training_command_preview.py --json` | Training command preview |
| `kimari-baseline-eval-plan.png` | `run_baseline_eval_plan.py --dry-run --json` | Baseline eval planning |
| `kimari-postrun-dryrun.png` | `postrun_private_sft.py --dry-run --json` | Post-training orchestration |
| `kimari-optimize-json.png` | `kimari optimize --profile test --json` | Performance optimization |
| `kimari-github-pages.png` | GitHub Pages landing | Landing page overview |

> These screenshots will be captured from a clean terminal environment. No real training outputs will be shown. No secrets or private paths will be visible. Screenshots are still **planned** — they have not been reviewed or committed yet.

---

## Safe Screenshot Capture

Before capturing terminal screenshots, review the [Safe Screenshot Capture Guide](SAFE_SCREENSHOT_CAPTURE.md). It covers:

- Cleaning your terminal before capture
- Removing private paths from output
- Avoiding tokens and secrets in screenshots
- No raw eval outputs
- No unreviewed benchmarks
- No HF tokens (see [HF Token Safety](HF_TOKEN_SAFETY.md))

Always review screenshots before committing.

---

## CLI Text Examples

Safe text blocks for generating captures are available in [docs/assets/screenshots/examples/](assets/screenshots/examples/). These `.txt` files contain clean CLI output without secrets, private paths, or benchmark claims.

Available examples:

- `kimari-setup-json.example.txt` — `kimari setup --json` output
- `kimari-preflight-private-sft.example.txt` — preflight check output
- `kimari-training-command-preview.example.txt` — training command preview
- `kimari-baseline-eval-plan.example.txt` — baseline eval plan
- `kimari-postrun-dryrun.example.txt` — postrun dry-run output

Generate new text blocks with:

```bash
python scripts/docs/generate_cli_screenshot_text.py --kind setup --json
```

---

## Screenshots Plan Script

A structured plan for capturing CLI screenshots is available via the `generate_safe_cli_screenshots_plan.py` script. This script does NOT generate images — it outputs a plan listing which commands to capture, with safety notes and metadata.

```bash
# View the plan as plain text
python scripts/docs/generate_safe_cli_screenshots_plan.py

# View the plan as JSON
python scripts/docs/generate_safe_cli_screenshots_plan.py --json

# View the plan as Markdown
python scripts/docs/generate_safe_cli_screenshots_plan.py --markdown

# Save the plan to a file
python scripts/docs/generate_safe_cli_screenshots_plan.py --json --output /tmp/screenshots-plan.json
```

The plan covers these commands:

1. `kimari status` — Server status
2. `kimari doctor --deep` — Extended diagnostics
3. `kimari gateway --plan` — Gateway endpoint plan
4. `kimari integrations generate --all` — Integration config snippets
5. `kimari benchmark --dry-run` — Benchmark dry-run plan
6. `kimari update check` — Update check

Each plan entry includes: command, description, category, safety notes, and status. All entries are `status: "planned"` — no actual screenshots are generated.

---

## Replacing Placeholders with Real Screenshots

When real captures become available from a GPU environment:

1. Follow the [Safe Screenshot Capture Guide](SAFE_SCREENSHOT_CAPTURE.md)
2. Replace placeholder references with actual image paths
3. Add images to `docs/assets/screenshots/` following naming conventions
4. Update this document to reference the real images
5. Do NOT include any secrets, tokens, or unreviewed benchmarks
6. No real training outputs should be visible in screenshots

Until real screenshots exist, use the text examples above as illustration.

---

## GTX 1060 Local Validation — Recommended Captures

These captures document the first real inference validation on GTX 1060 hardware.

### 1. nvidia-smi on WSL2

**Command:** `nvidia-smi`
**Purpose:** Shows GPU detection, driver version, CUDA version in WSL2
**Safety:** Ensure no process details with private paths are visible
**Status:** planned

### 2. kimari doctor --deep

**Command:** `kimari doctor --deep`
**Purpose:** Shows diagnostic output including CUDA/NVIDIA detection, compute capability
**Safety:** May show local paths — sanitize before committing
**Status:** planned

### 3. llama-server CUDA startup

**Command:** `llama-server -m <model> --port 8081`
**Purpose:** Shows CUDA initialization, compute capability detection, model loading
**Safety:** Model path is OK to show (it's in models/ directory)
**Status:** planned

### 4. Health endpoint check

**Command:** `curl http://127.0.0.1:8081/health`
**Purpose:** Confirms inference server is running and healthy
**Safety:** No secrets in health endpoint response
**Status:** planned

### 5. Token/s generation output

**Command:** llama-server output during generation
**Purpose:** Shows prompt eval and generation speed (tok/s)
**Safety:** No secrets in performance metrics
**Status:** planned

---

## Rules

1. **No secrets** — API keys, tokens, local paths, or user names must not appear.
2. **No real training outputs** — Loss curves, adapter weights, and raw eval outputs stay local.
3. **No real benchmarks** — Benchmark claims require measured, reviewed data.
4. **Kimari-4B not released** — Screenshots must not imply the model is available.
5. **No real screenshots without review** — Do not commit screenshot images until they have been manually reviewed for safety (no tokens, no private paths, no unreviewed benchmarks).
6. **Optimize image size** — Compress PNGs, prefer WebP for large images.
7. **Alt text required** — Every image must have descriptive alt text.
8. **Illustrative only** — Code blocks in this doc are examples, not actual outputs.
