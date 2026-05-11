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
| `kimari-setup-json.png` | `kimari setup --json` | Environment detection output |
| `kimari-preflight-private-sft.png` | `preflight_private_sft.py --json` | Preflight check results |
| `kimari-training-command-preview.png` | `run_training_command_preview.py --json` | Training command preview |
| `kimari-baseline-eval-plan.png` | `run_baseline_eval_plan.py --dry-run --json` | Baseline eval planning |
| `kimari-postrun-dryrun.png` | `postrun_private_sft.py --dry-run --json` | Post-training orchestration |
| `kimari-optimize-json.png` | `kimari optimize --profile test --json` | Performance optimization |
| `kimari-github-pages.png` | GitHub Pages landing | Landing page overview |

> These screenshots will be captured from a clean terminal environment. No real training outputs will be shown. No secrets or private paths will be visible.

---

## Safe Screenshot Capture

Before capturing terminal screenshots, review the [Safe Screenshot Capture Guide](SAFE_SCREENSHOT_CAPTURE.md). It covers:

- Cleaning your terminal before capture
- Removing private paths from output
- Avoiding tokens and secrets in screenshots
- No raw eval outputs
- No unreviewed benchmarks

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

## Rules

1. **No secrets** — API keys, tokens, local paths, or user names must not appear.
2. **No real training outputs** — Loss curves, adapter weights, and raw eval outputs stay local.
3. **No real benchmarks** — Benchmark claims require measured, reviewed data.
4. **Kimari-4B not released** — Screenshots must not imply the model is available.
5. **Optimize image size** — Compress PNGs, prefer WebP for large images.
6. **Alt text required** — Every image must have descriptive alt text.
7. **Illustrative only** — Code blocks in this doc are examples, not actual outputs.
