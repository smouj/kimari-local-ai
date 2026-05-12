# HF Jobs Micro SFT Real Run

> First real micro SFT training run for Kimari-4B on Hugging Face Jobs.

## Objective

Run a short LoRA fine-tuning job on a10g-small GPU to validate the full training pipeline:
dataset → training → adapter → summary.

## What This Is

- **First real training** for Kimari-4B
- **Micro SFT** with 72 examples, max 20 steps
- **LoRA r=8** on Qwen2.5-3B-Instruct (Apache 2.0)
- **Private** — adapter stays in ephemeral HF Jobs storage
- **Not committed** to git
- **Not uploaded** to Hugging Face

## What This Is NOT

❌ No public release of Kimari-4B
❌ No adapter committed to git
❌ No GGUF generated
❌ No HF upload
❌ No checkpoint download (ephemeral storage)
❌ No benchmark claims

## Commands

```bash
# 1. Check HF Jobs access
python training/scripts/check_hf_jobs_access.py --json

# 2. Dry-run (default)
python training/scripts/hf_jobs_micro_sft_real.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft_real.v0.yaml \
    --dry-run --json

# 3. Print command
python training/scripts/hf_jobs_micro_sft_real.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft_real.v0.yaml \
    --print-command

# 4. Real submission (requires explicit consent)
python training/scripts/hf_jobs_micro_sft_real.py \
    --config training/configs/hf_jobs_kimari4b_micro_sft_real.v0.yaml \
    --require-jobs-access --allow-submit --yes
```

## Configuration

| Parameter | Value |
|-----------|-------|
| Base model | Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0) |
| Dataset | kimari-fit-v0 (72 examples) |
| Method | SFT LoRA r=8, alpha=16 |
| Max steps | 10 |
| Flavor | a10g-small ($1.00/hour) |
| Timeout | 20 minutes |
| Estimated cost | ~$0.35 |

## Safety Flags

| Flag | Value |
|------|-------|
| training_performed | true (this IS training) |
| adapter_generated | true (adapter WILL be created) |
| adapter_committed | false (NEVER commit) |
| hf_upload_performed | false |
| push_to_hub | false |
| gguf_export | false |
| report_to | none |
| gate_state | BLOCKED |

## Artifact Policy

| Artifact | Committed | Uploaded | Persisted |
|----------|-----------|----------|-----------|
| Config YAML | ✅ Yes | ❌ No | N/A |
| Runner script | ✅ Yes | ❌ No | N/A |
| Dataset JSONL | ✅ Yes | ❌ No | N/A |
| Summary JSON | ✅ Yes | ❌ No | N/A |
| Adapter .safetensors | ❌ No | ❌ No | ❌ Ephemeral |
| Training logs | ❌ No | ❌ No | ❌ Ephemeral |
| Checkpoints | ❌ No | ❌ No | ❌ Ephemeral |

## Limitations

- **Adapter is ephemeral**: HF Jobs storage is temporary. The adapter generated in this run will be lost when the job completes. This is intentional — we're validating the pipeline, not producing a persistent adapter.
- **No persistent storage**: To persist the adapter, we would need to either upload it to HF (which we're not doing) or download it locally (which requires a more complex setup).
- **This is validation, not production**: The resulting adapter, if it exists, is not suitable for public release.

## Gate

**BLOCKED** — No automatic transitions. Even if training succeeds, gate stays BLOCKED until manual review.

See [KIMARI4B_RELEASE_GATE.md](KIMARI4B_RELEASE_GATE.md) for state transitions.