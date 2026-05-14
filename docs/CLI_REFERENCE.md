# Kimari CLI Reference

Complete reference for all Kimari CLI commands.

> For installation and quick start, see [INSTALL_ONE_COMMAND.md](INSTALL_ONE_COMMAND.md) or the main [README](../README.md).

---

## Diagnostics & Info

```bash
kimari doctor                                        # System diagnostics (CUDA, GPU, llama-server)
kimari doctor --deep                                 # 14 deep diagnostic checks (Python, version, paths, config, models, packaged defaults, llama-server, CUDA/NVIDIA, default profile, secret scanner, benchmark prompts, gateway module, integration docs, preview gate)
kimari doctor --deep --json                         # Deep diagnostics as JSON
kimari doctor --json                                 # JSON output for automation/IDEs
kimari info                                          # Installation info (version, paths, profiles)
kimari info --json                                   # JSON info output
```

## Server Management

```bash
kimari start                                         # Start server (default: test profile)
kimari start --profile gtx1080                       # Start with a specific GPU profile
kimari start --dry-run                               # Preview command without running
kimari start --host 0.0.0.0 --port 8080              # Override host and port
kimari start --daemon                                # Start in background
kimari stop                                          # Stop running server
kimari status                                        # Check server status
kimari status --json                                 # JSON status output
kimari logs                                          # Show server logs
kimari logs --follow                                 # Tail logs in real time
```

## Models

```bash
kimari pull test                                      # Download test model (TinyLlama 1.1B)
kimari pull recommended                               # Download recommended model (Qwen3-4B)
kimari pull --all                                     # Download all available models
kimari pull --list                                    # List available models in registry
kimari pull test --dry-run                            # Preview download (no transfer)
kimari models                                         # List downloaded models
kimari models --json                                  # JSON model listing
kimari models --downloaded                            # Show only downloaded models
```

> **SHA256 verification:** `kimari pull` supports SHA256 hash verification after download. However, model hashes in the registry are **not yet pinned** — verification is supported but not currently enforced. This will be updated in a future release.

## Model Hash Verification

```bash
kimari models hash <path>                 # Compute SHA256 hash of a local GGUF file
kimari models hash <path> --json          # JSON output
kimari models verify <model-id-or-path>   # Verify model hash against registry
kimari models verify <model-id> --json    # JSON output
kimari models pin-hash <model-id>                # Preview pinning hash (dry-run)
kimari models pin-hash <model-id> --dry-run      # Preview patch without writing
kimari models pin-hash <model-id> --write         # Write with confirmation
kimari models pin-hash <model-id> --write --yes   # Write without prompt
```

> **Note:** SHA256 hashes in the registry are not yet pinned. `kimari models verify` will report "hash not pinned" until hashes are explicitly set. Use `pin-hash --write` to compute and pin real hashes. Use `--dry-run` to preview the patch, `--yes` to skip the confirmation prompt.

See [MODEL_HASHING.md](MODEL_HASHING.md) for the full workflow.

## Profiles & Configuration

```bash
kimari profiles                                       # List GPU profiles
kimari profiles --json                                # JSON profile output
kimari config path                                    # Print config file path
kimari config show                                    # Display full configuration
kimari config show --json                             # JSON config output
kimari config validate                                # Validate config against schema
kimari config migrate                                 # Migrate config to current version
kimari config migrate --dry-run                       # Preview migration changes
```

### Packaged Defaults & User Paths

Kimari works when installed from PyPI — no need to run from the repo root:

- **Config** lives in your user config directory (`~/.config/kimari/` on Linux/macOS, `%APPDATA%\Kimari\` on Windows)
- **State** (PID, logs, tokens) lives in your user state directory
- **Models** are stored in your user data directory
- **Packaged defaults** ship inside the wheel and are copied to your user config on first use

```bash
kimari config path                         # Show where your config lives
export KIMARI_HOME=~/.kimari               # Override all paths at once
export KIMARI_CONFIG_DIR=/etc/kimari       # Override config dir only
```

### Model Path Resolution

`resolve_model_path()` locates model files by searching in order:

1. **Absolute path** — used as-is if the model path is already absolute
2. **CWD-relative** — resolved relative to the current working directory
3. **User models dir** — the platform-specific user data models directory
4. **Repo-root** — the `models/` directory under the project root (editable installs)
5. **Fallback** — returns the original path if nothing is found

## Chat & Benchmarks

```bash
kimari chat "Your message here"                       # Send a single message
kimari chat                                          # Interactive chat mode
kimari bench --profile test                           # Run benchmarks (tokens/s, TTFT)
kimari bench --profile gtx1080 --vram 8.0             # Override VRAM manually
kimari bench --profile test --json                    # JSON benchmark output
kimari fit --model models/file.gguf --ctx 8192        # Calculate KimariFit score
kimari fit --model models/file.gguf --vram 8.0        # Override VRAM for KimariFit
```

## Guided Setup

```bash
kimari setup                              # Detect environment and recommend configuration
kimari setup --json                       # JSON output for automation
kimari setup --write                      # Persist detected configuration to user config dir
kimari setup --write --yes                # Non-interactive: shows preview, writes without prompt
kimari setup --integration openclaw       # Recommend OpenClaw integration
kimari setup --integration hermes         # Recommend Hermes integration
kimari setup --integration continue       # Recommend Continue IDE integration
kimari setup --dry-run                    # Preview without detection
```

With `--write`, Kimari persists the recommended profile, integration settings, and hardware summary to your user config directory. A timestamped backup is created before any changes.

### Recovering from Incomplete Setup Config

If `kimari doctor --deep` warns about an incomplete user config (missing `version`, `profiles`, or `default_profile`), you can regenerate a safe, complete configuration:

```bash
kimari setup --write --yes --reset-user-config
```

This flag regenerates the user config from packaged defaults, creating a timestamped backup of the existing config first. Use this when a previous `kimari setup --write` produced an incomplete configuration due to the empty-dict bug fixed in v0.1.38-alpha.

## Performance Tuning

### `kimari optimize`

Analyzes your profile and recommends optimal settings for VRAM, context, batch sizes, and cache types:

```bash
kimari optimize                              # Analyze default profile
kimari optimize --profile gtx1060            # Optimize for GTX 1060
kimari optimize --profile test --mode fast   # Fast mode recommendations
kimari optimize --profile test --json        # JSON output for automation
```

### `kimari perf`

Shows a performance matrix across all modes (safe, balanced, fast, ide, agent):

```bash
kimari perf --profile test --dry-run         # Default mode overview
kimari perf --profile gtx1060 --matrix       # All modes compared
kimari perf --profile test --json --dry-run  # JSON output
```

### `kimari benchmark`

Generate a benchmark plan without executing models (dry-run by default):

```bash
kimari benchmark --dry-run                        # Show estimated plan for default profile
kimari benchmark --profile gtx1060-safe --dry-run # Plan for a specific profile
kimari benchmark --matrix --dry-run --json        # Full parameter matrix as JSON
kimari benchmark --measure --endpoint <url> --model <name> --yes  # Measured benchmark against running server (--yes required)
kimari benchmark --measure --endpoint <url> --model <name> --yes --output results.json  # Save results to file
```

### `kimari tune`

Get recommended settings based on VRAM/RAM estimation:

```bash
kimari tune --dry-run                       # Recommendations for default profile
kimari tune --profile gtx1060-safe --json   # JSON output for automation
```

> **Note:** `kimari tune --apply` is intentionally **blocked**. Auto-apply will be enabled once measured benchmarks are validated.

See [PERFORMANCE_TUNING_PLAN.md](PERFORMANCE_TUNING_PLAN.md) for the full measurement and tuning roadmap.

### Performance Profiles

| Profile | GPU | Mode | Cache | Context | Use Case |
|---------|-----|------|-------|---------|----------|
| `gtx1060-safe` | GTX 1060 | safe | q8_0/q8_0 | 4,096 | Maximum stability, no OOM |
| `gtx1060-fast` | GTX 1060 | fast | q8_0/q8_0 | 8,192 | Speed priority |
| `gtx1080-balanced` | GTX 1080 | balanced | q8_0/f16 | 8,192 | Quality/speed balance |
| `gtx1080-longctx` | GTX 1080 | balanced | q8_0/q8_0 | 16,384 | Long conversations |
| `ide-local` | Any 6 GB+ | ide | q8_0/q8_0 | 4,096 | Continue, Cursor, VS Code |
| `agent-local` | Any 6 GB+ | agent | q8_0/q8_0 | 4,096 | OpenClaw, Hermes |
| `openclaw-local` | Any 6 GB+ | agent | q8_0/q8_0 | 4,096 | OpenClaw integration |
| `hermes-local` | Any 6 GB+ | agent | q8_0/q8_0 | 4,096 | Hermes Agent integration |

> All new profiles use TinyLlama during alpha. When Kimari-4B is released, the GPU-specific profiles will use it by default.

## Token Management

```bash
kimari token create                       # Generate a local auth token
kimari token show                         # Display the current token
kimari token delete                       # Remove the token
```

> **Note:** These tokens are prepared for future Kimari API / reverse proxy use. `llama-server` does not apply auth natively.

## Gateway Dashboard

```bash
kimari gateway setup                      # Install dashboard deps, setup SQLite, build
kimari gateway start --open               # Start local dashboard at 127.0.0.1:3105
kimari gateway status --json              # Dashboard + backend reachability + gate state
kimari gateway logs --lines 50            # Recent dashboard logs
kimari gateway stop                       # Stop dashboard
```

> The Dashboard is implemented and localhost-only by default. The management Gateway API remains planned at `127.0.0.1:11436`. Normal users should use the CLI — no `npm` needed.

See [GATEWAY_DASHBOARD.md](GATEWAY_DASHBOARD.md) for details.

## Update Check

```bash
kimari update check                       # Show current version (offline)
kimari update check --online              # Check GitHub for latest release
kimari update check --json                # JSON output
```

> **Note:** Kimari never auto-updates. `--online` checks GitHub only when explicitly requested. See [UPDATE.md](UPDATE.md) for details.

## Integration Config Generator

```bash
kimari integrations generate --target openwebui --json   # Open WebUI config snippet
kimari integrations generate --target openclaw --json    # OpenClaw config snippet
kimari integrations generate --target hermes --json      # Hermes agent config snippet
kimari integrations generate --target continue --json    # Continue.dev config snippet
kimari integrations generate --all --json                # All integration configs
```

> Configs contain no tokens or API keys. Default base_url is `http://127.0.0.1:11435/v1` (localhost only). Use `--write --output /path/to/file.json` to save to a specific path.

See [INTEGRATION_CONFIG_GENERATOR.md](INTEGRATION_CONFIG_GENERATOR.md) for details.

## Runtime Flag Validation

```bash
kimari start --dry-run --strict-flags     # Fail on unsupported flags
```

Without `--strict-flags`, unsupported flags produce warnings. With it, they cause an error.

## Experimental API

```bash
pip install "kimari-local-ai[api]"
kimari api --experimental
# Listens on http://127.0.0.1:11436
```

> ⚠️ **Experimental** — This API may change or be removed without notice. Not for production use.

See [API_EXPERIMENTAL.md](API_EXPERIMENTAL.md) for details.

## Windows Install

PowerShell scripts for building, installing, and testing on Windows:

```powershell
.\scripts\windows\build-wheel.ps1
.\scripts\windows\install-from-wheel.ps1
.\scripts\windows\install-from-testpypi.ps1
```

See [scripts/windows/README.md](../scripts/windows/README.md) for details.

## Benchmark Submissions

Share benchmark results with the community using the standardized format. Submit via PR to `benchmarks/results/`.

See [BENCHMARK_SUBMISSIONS.md](BENCHMARK_SUBMISSIONS.md) for the community workflow and format.

## KimariFit Score

The KimariFit formula measures useful intelligence density per GiB of VRAM.

```
M_total ≈ S_GGUF + C/9709 + overhead
```

| Score | Rating | Meaning |
|:-----:|--------|---------|
| 90–100 | 🟢 **Optimal** | Model fits perfectly. Best performance expected. |
| 70–89 | 🟡 **Good** | Minor compromises. Works well for most tasks. |
| 50–69 | 🟠 **Usable** | Significant quantization. Acceptable for basic use. |
| < 50 | 🔴 **Poor** | Will be slow or OOM. Not recommended. |

```bash
kimari fit --model models/your-model.gguf --ctx 8192
kimari fit --model models/your-model.gguf --vram 8.0
```

See [00-02_kimarifit_formula.md](00-02_kimarifit_formula.md) for the full formula and methodology.
