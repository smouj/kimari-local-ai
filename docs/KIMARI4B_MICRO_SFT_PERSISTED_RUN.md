# Kimari-4B Micro SFT Persisted Run

> Second micro SFT run on HF Jobs with private adapter persistence.

## Objective

Repeat the micro SFT training on HF Jobs, but this time **persist the adapter to a private Hugging Face model repository** for internal evaluation. The adapter will NOT be committed to the public repo or released publicly.

## Key Difference from v0.1.49

| Aspect | v0.1.49 (First Run) | v0.1.51 (Persisted Run) |
|--------|---------------------|-------------------------|
| Adapter persistence | Ephemeral (`/tmp/`) | Private HF repo |
| Adapter retrieval | None | `huggingface_hub.upload_folder()` |
| Private repo | Not created | `Smouj013/kimari4b-micro-sft-adapter-v0` |
| Load check | Not performed | Basic load + generate test |
| Steps | 10 | 20 |

## Configuration

| Parameter | Value |
|-----------|-------|
| Run ID | `kimari4b-hfjobs-micro-sft-persisted-v0` |
| Base model | Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0) |
| Flavor | a10g-small ($1.00/hr) |
| Docker | pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel |
| Max steps | 20 |
| LoRA r | 8, alpha 16 |
| Dataset | kimari-fit-v0 (72 examples) |
| Dataset SHA256 | `f8ce140b5e2e127e4324f3a7c4785480...` |
| Timeout | 30 minutes |
| Private repo | `Smouj013/kimari4b-micro-sft-adapter-v0` |
| Estimated cost | ~$0.50 |

## Safety

| Flag | Value | Notes |
|------|-------|-------|
| `public_release_allowed` | false | Never |
| `hf_public_upload_allowed` | false | Never |
| `gguf_export_allowed` | false | Never |
| `adapter_committed_public` | false | Never |
| `push_to_hub` (trainer) | false | Explicit upload only |
| `private_adapter_persistence_allowed` | true | Upload to private repo |
| `report_to` | none | No WandB/MLflow |
| `preview_gate_state` | BLOCKED | No auto transition |

## Commands

```bash
# Dry-run (default, safe)
python training/scripts/hf_jobs_micro_sft_persisted.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft_persisted.v0.yaml \
    --dry-run --json

# Print command without submitting
python training/scripts/hf_jobs_micro_sft_persisted.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft_persisted.v0.yaml \
    --print-command

# Submit real job (requires --allow-submit --yes)
python training/scripts/hf_jobs_micro_sft_persisted.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft_persisted.v0.yaml \
    --require-jobs-access \
    --allow-submit \
    --yes

# Check status
python training/scripts/hf_jobs_status.py \
    --job-id <JOB_ID> \
    --logs --sanitize-logs --tail 200

# Create summary
python training/scripts/create_hf_jobs_micro_sft_persisted_summary.py \
    --job-id <JOB_ID> \
    --status completed \
    --output docs/assets/results/hf_jobs_micro_sft_persisted_summary.json \
    --json

# Validate summary
python training/scripts/validate_hf_jobs_micro_sft_persisted_summary.py \
    --summary docs/assets/results/hf_jobs_micro_sft_persisted_summary.json \
    --json
```

## Expected Results

```json
{
  "run_id": "kimari4b-hfjobs-micro-sft-persisted-v0",
  "status": "completed",
  "training_performed": true,
  "adapter_generated": true,
  "adapter_persisted_private": true,
  "adapter_committed_public": false,
  "hf_public_upload_performed": false,
  "gguf_generated": false,
  "gate_state": "BLOCKED"
}
```

## Private vs Public Upload

- **Private upload** (`private_adapter_persistence_allowed=true`): Upload to `Smouj013/kimari4b-micro-sft-adapter-v0` (private repo). This is intentional and controlled.
- **Public upload** (`hf_public_upload_allowed=false`): Never upload to any public repository. The trainer's `push_to_hub` is disabled; only explicit private upload happens after training.

## Gate

**BLOCKED** — No automatic gate transition even with adapter persistence.