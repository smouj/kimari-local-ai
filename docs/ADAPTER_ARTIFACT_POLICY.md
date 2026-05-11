# Adapter Artifact Policy — Kimari Private Training

> **Document Type:** Artifact handling policy  
> **Version:** v0.1.20-alpha  
> **Date:** 2026-05-22  
> **Status:** Active — governs all adapter artifacts from private training runs

---

## What Is a Private Adapter

A **private adapter** is a LoRA (Low-Rank Adaptation) weight set produced by fine-tuning a base model on the Kimari dataset. It contains the learned delta weights that, when merged with the base model, produce the fine-tuned Kimari behavior.

Private adapters are:

- **Produced locally** — on the developer's GPU hardware during training
- **Stored locally** — in the `training/adapters/` directory, which is gitignored
- **Not published** — not uploaded to Hugging Face, any other platform, or shared publicly
- **Not committed** — the adapter weights, optimizer states, and training checkpoints are never committed to the Git repository
- **Subject to the ADAPTER_PREVIEW_GATE** — any transition toward public visibility requires explicit approval (see `docs/ADAPTER_PREVIEW_GATE.md`)

---

## Where Adapters Are Stored Locally

Adapters are stored under the `training/adapters/` directory:

```
training/adapters/
├── .gitkeep
├── kimari-smollm3-sft-v0/
│   ├── adapter_model.safetensors    # LoRA adapter weights (NOT committed)
│   ├── adapter_config.json          # LoRA configuration
│   ├── tokenizer.json               # Tokenizer from base model
│   ├── tokenizer_config.json        # Tokenizer configuration
│   ├── special_tokens_map.json      # Special tokens mapping
│   ├── trainer_state.json           # Training state (loss, lr, etc.)
│   ├── training_args.bin            # Training arguments snapshot
│   ├── all_results.json             # Summary of training results
│   └── runs/                        # Internal checkpoint subdirectories
│       ├── checkpoint-500/
│       ├── checkpoint-1000/
│       └── ...
└── kimari-smollm3-orpo-v0/
    ├── adapter_model.safetensors    # ORPO adapter weights (NOT committed)
    ├── adapter_config.json
    └── ...
```

The `training/adapters/` directory is excluded from Git via `.gitignore` patterns for `training/adapters/` and `training/runs/`.

---

## What NOT to Commit

The following artifacts must **never** be committed to the Git repository:

| Artifact | Reason | Gitignore Pattern |
|----------|--------|-------------------|
| `adapter_model.safetensors` | Binary weight data — large, proprietary, not for distribution | `training/adapters/**/*.safetensors` |
| `adapter_model.bin` | Legacy weight format — same concerns as safetensors | `training/adapters/**/*.bin` |
| Optimizer states (`optimizer.pt`, `rng_state.pth`) | Training state — not needed for inference, contains no useful information | `training/adapters/**/*.pt` |
| Training checkpoints (`checkpoint-*/`) | Intermediate states — redundant with final adapter, large | `training/adapters/**/checkpoint-*/` |
| Heavy log files (`trainer_log.jsonl` if large) | Potentially large, not useful for repository consumers | `training/adapters/**/*.log` |
| `wandb/` directory | Weights & Biases local cache — contains experiment data, may contain API keys | `wandb/` |
| TensorBoard logs (`runs/`) | Binary event files — not useful in Git, viewable locally | `training/adapters/**/runs/` |
| `training_args.bin` | Binary training arguments — not human-readable, redundant with config | `training/adapters/**/*.bin` |
| Scheduler states (`scheduler.pt`) | Training state — not needed post-training | `training/adapters/**/*.pt` |
| Training data copies | License restrictions; data should come from `dataset/build/` | `training/adapters/**/*.jsonl` |

---

## What CAN Be Committed

The following lightweight, non-weight artifacts **may** be committed to the repository:

| Artifact | Conditions | Purpose |
|----------|-----------|---------|
| **Adapter manifest without weights** | Must NOT contain weight data; only metadata | Records adapter name, base model, training config, date, and status |
| **`adapter_config.json`** | Must NOT contain weight tensors; only LoRA configuration (rank, alpha, target modules, etc.) | Documents the adapter architecture for reproducibility |
| **Eval summary (anonymized)** | Must NOT contain prompt text or full model responses; only scores and category breakdowns | Records evaluation outcomes without exposing eval content |
| **Hashes** | Must be SHA-256 hashes of the actual weight files, verified locally | Provides integrity verification for adapter files |
| **Training config** | Must reference the YAML config used, not duplicate training data | Links the adapter to the configuration that produced it |
| **Run manifest** | Must be a YAML file with metadata only (see `training/configs/private_sft_run.v0.yaml`) | Tracks the run status, dates, and references |

**Important:** A manifest CAN be committed if it doesn't contain sensitive paths or weights. Adapter files (weights, optimizer states, checkpoints) must NEVER be committed — see the "What NOT to Commit" section above.

---

## Adapter Naming Convention

Adapters follow a strict naming convention:

| Name | Type | Description |
|------|------|-------------|
| `kimari-smollm3-sft-v0` | SFT adapter | First supervised fine-tuning adapter on SmolLM3-3B |
| `kimari-smollm3-orpo-v0` | ORPO adapter | First preference tuning adapter (runs after SFT) |

**Naming rules:**

- Format: `kimari-<base>-<method>-v<version>`
- `<base>`: the short name of the base model (e.g., `smollm3`)
- `<method>`: the fine-tuning method (`sft` or `orpo`)
- `<version>`: zero-indexed integer starting at `v0`
- Subsequent iterations increment the version: `v0`, `v1`, `v2`, etc.
- The version tracks the adapter iteration, not the project version

**Directory paths:**

- SFT: `training/adapters/kimari-smollm3-sft-v0/`
- ORPO: `training/adapters/kimari-smollm3-orpo-v0/`

---

## Adapter Manifest Format

When creating an adapter manifest, use the template at `training/templates/adapter_manifest.template.yaml` and the `create_adapter_manifest.py` script:

```bash
python training/scripts/create_adapter_manifest.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --output training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml
```

The script:
- Reads the template from `training/templates/adapter_manifest.template.yaml`
- Fills in values from the run config and adapter directory
- Computes SHA-256 hashes of allowed files (skips `.safetensors`, `.bin`, `.pt`, etc.)
- Sets `preview_gate_state: BLOCKED`, `public_release_allowed: false`, `hf_upload_allowed: false`
- Lists suspicious files (weights) but does NOT include their content

Preview with `--dry-run` before writing:

```bash
python training/scripts/create_adapter_manifest.py \
    --run-config training/configs/private_sft_run.v0.yaml \
    --adapter-dir training/adapters/kimari-smollm3-sft-v0 \
    --dry-run
```

The manifest CAN be committed to the repository if it doesn't contain sensitive paths or weights. Adapter files themselves must NEVER be committed.

Manual manifest format (if not using the script):

```yaml
# training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml
adapter_name: kimari-smollm3-sft-v0
base_model: HuggingFaceTB/SmolLM3-3B
base_model_license: Apache-2.0
method: sft
lora_config:
  r: 32
  alpha: 64
  dropout: 0.05
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
training_config: training/configs/kimari_sft_lora.v0.example.yaml
dataset_build: dataset/build/kimari-v0/
training_date: "2026-05-22"  # Update with actual date
status: private  # One of: private, pending_preview, approved_preview
preview_gate_state: BLOCKED  # See docs/ADAPTER_PREVIEW_GATE.md
hashes:
  adapter_model_sha256: ""  # Fill with actual SHA-256 after training
  adapter_config_sha256: ""  # Fill with actual SHA-256 after training
notes: "First private SFT adapter. No public release authorized."
```

---

## Hash Recording for Integrity

SHA-256 hashes must be recorded for all adapter weight files after training completes. This ensures:

1. **Integrity verification** — You can confirm the adapter has not been corrupted or modified
2. **Reproducibility** — Future runs can be verified against the same hash
3. **Audit trail** — Hashes provide a record of what was produced, even if the weights themselves are not shared

**How to compute hashes:**

```bash
# Compute SHA-256 hash for adapter weights
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_model.safetensors

# Compute hash for adapter config
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_config.json
```

**Recording hashes:**

Record hashes in the adapter manifest (`MANIFEST.yaml`) and optionally in a project-level hash record. Only the hash strings are committed — never the files being hashed.

**Verification:**

```bash
# Verify adapter integrity after transfer or backup
echo "expected_hash  training/adapters/kimari-smollm3-sft-v0/adapter_model.safetensors" | sha256sum -c
```

---

## Release Gate

No adapter (SFT or ORPO) may be published, shared, or uploaded to any platform without passing through the release gate defined in `docs/ADAPTER_PREVIEW_GATE.md`.

**Summary of the gate states:**

| State | Meaning |
|-------|---------|
| `BLOCKED` | Default. No sharing, no upload, no public visibility |
| `PENDING` | License verified, no secrets/data issues, size/hash recorded |
| `APPROVED_FOR_PRIVATE_TESTING` | Baseline comparison done, manual review done, no safety regression |
| `APPROVED_FOR_PUBLIC_PREVIEW` | Model card updated, HF placeholder reviewed, safety review passed |

All transitions require explicit human decision. There are no automatic transitions.

---

## Backup and Transfer

### Local Backup

Adapters should be backed up locally (e.g., to an external drive or private cloud storage) after training:

```bash
# Example: backup adapter to external drive
cp -r training/adapters/kimari-smollm3-sft-v0/ /mnt/backup/kimari-adapters/

# Verify backup integrity
sha256sum training/adapters/kimari-smollm3-sft-v0/adapter_model.safetensors
sha256sum /mnt/backup/kimari-adapters/kimari-smollm3-sft-v0/adapter_model.safetensors
```

### Transfer Between Machines

If the adapter needs to be transferred to another machine for evaluation:

1. Use a secure, private method (e.g., `scp`, private S3 bucket, encrypted USB)
2. Do not use public URLs, public file sharing services, or unencrypted channels
3. Verify hashes on the receiving machine after transfer
4. Delete the adapter from intermediate storage after transfer is confirmed

---

## v0.1.22-alpha Additions

The following references were introduced in v0.1.22-alpha to strengthen artifact handling and post-run orchestration:

- **[docs/PRIVATE_RUN_ARTIFACTS.md](PRIVATE_RUN_ARTIFACTS.md)** — Provides detailed classification of all artifacts produced by private training runs, including which artifacts are safe to commit, which must remain local, and how to handle edge cases. Refer to this document for the definitive artifact classification beyond the summary tables in this policy.

- **[`training/scripts/postrun_private_sft.py`](../training/scripts/postrun_private_sft.py)** — Orchestrates post-training steps including eval execution, summary generation, manifest creation, and ORPO decision checks. This script helps enforce the artifact policy automatically after a training run completes.

### Pre-commit Checklist for Summaries

Before committing any eval summary or adapter metadata to the repository, verify **all** of the following:

- [ ] **No raw prompts** — Summary must not contain prompt text from the evaluation suite
- [ ] **No local paths** — No absolute paths (e.g., `/home/user/…`) or machine-specific directory references
- [ ] **No tokens or secrets** — No API keys, auth tokens, or credentials of any kind
- [ ] **No unreviewed benchmark claims** — All scores must be marked `manual_review_required` until a human has reviewed and approved them

If any of these checks fail, do **not** commit the file. Sanitize or regenerate the summary first.

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine governing adapter visibility and release |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Plan for evaluating base model before SFT |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Step-by-step runbook for first private SFT |
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | Formal acceptance record for SmolLM3-3B |
| [MODEL_HASHING.md](MODEL_HASHING.md) | SHA-256 hash procedures for model files |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full release process for when public release is authorized |
| [HF_PLACEHOLDER_PLAN.md](HF_PLACEHOLDER_PLAN.md) | Plan for Hugging Face placeholder repository |
| [PRIVATE_RUN_ARTIFACTS.md](PRIVATE_RUN_ARTIFACTS.md) | Detailed artifact classification for private training runs |
| [training/templates/adapter_manifest.template.yaml](../training/templates/adapter_manifest.template.yaml) | Template for adapter manifest creation |

---

*This policy governs the handling of all adapter artifacts from private training runs. No weights, optimizer states, checkpoints, or training data may be committed to the repository. Only lightweight metadata, configs, anonymized summaries, and hashes may be committed. All adapters start in the BLOCKED state and require explicit human approval before any form of distribution.*
