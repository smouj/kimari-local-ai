# Kimari-4B Next Run Plan

> Plan for the second micro SFT run with adapter persistence.

## Objective

Execute a second micro SFT run that **retrieves the adapter** from HF Jobs ephemeral storage, enabling baseline vs adapter evaluation.

## Previous Run Summary

| Field | Value |
|-------|-------|
| Job ID | 6a038ec87618f125ee2b7984 |
| Status | COMPLETED |
| GPU | NVIDIA A10G, 22.3 GB |
| Base model | Qwen/Qwen2.5-1.5B-Instruct |
| Steps | 10/10 |
| Loss | 2.62 → 3.19 |
| Adapter | Generated but ephemeral (not retrieved) |
| Cost | ~$0.35 |

## Recommended Next Run Parameters

| Parameter | Value | Reason |
|-----------|-------|--------|
| Base model | Qwen/Qwen2.5-1.5B-Instruct | Same as v0.1.49, proven working |
| Flavor | a10g-small | $1.00/hour, proven |
| Docker | pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel | Proven working stack |
| Max steps | 20 | Slightly more than v0.1.49 |
| Dataset | kimari-fit-v0 (72 examples) | Same dataset |
| LoRA r | 8 | Same config |
| Timeout | 20 min | Same timeout |
| Cost cap | $0.50 | Conservative |

## Key Changes from v0.1.49

1. **Adapter retrieval**: Upload adapter to private HF Hub repo after training
2. **Full dataset**: Use all 72 examples instead of 3 inline
3. **Baseline eval**: Run baseline (no adapter) eval before SFT
4. **Adapter eval**: Run adapter eval after SFT

## Adapter Retrieval Strategy

Use `huggingface_hub.HfApi.upload_folder()` to push adapter to private repo:

```python
from huggingface_hub import HfApi
api = HfApi()
repo_id = "Smouj013/kimari4b-micro-sft-adapter-v0"
api.create_repo(repo_id=repo_id, private=True, exist_ok=True)
api.upload_folder(
    folder_path="/tmp/kimari4b-micro-sft-adapter",
    repo_id=repo_id,
    commit_message="Micro SFT v0 adapter",
)
```

## Safety Constraints (same as v0.1.49)

- `push_to_hub: false` in training config (upload happens explicitly, not via Trainer)
- `adapter_committed: false` (never to public repo)
- `hf_upload_performed: false` in safety flags
- Gate stays BLOCKED
- No GGUF generation
- No public release

## Cost Estimate

| Component | Cost |
|-----------|------|
| Training (20 steps, a10g-small, ~15 min) | ~$0.25 |
| Baseline eval (~5 min) | ~$0.08 |
| Adapter eval (~5 min) | ~$0.08 |
| **Total** | **~$0.41** |

## Gate

**BLOCKED** — No automatic gate transition even if adapter is retrieved.