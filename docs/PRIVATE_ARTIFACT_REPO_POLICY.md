# Private Artifact Repository Policy

> Policy for the `smouj/kimari-4b-artifacts` private repository.

## Purpose

This private repository stores Kimari-4B training artifacts that must NOT be in the public `smouj/kimari-local-ai` repo.

## What CAN Go Here

| Artifact | Format | Location |
|----------|--------|----------|
| LoRA adapter weights | `.safetensors` (Git LFS) | `adapters/<run-id>/` |
| Training result summaries | `.json` (sanitized) | `training/results/` |
| Baseline eval results | `.json` (sanitized) | `eval/baselines/` |
| Adapter vs baseline comparisons | `.json` (sanitized) | `eval/comparisons/` |
| Adapter manifests | `.json` | `adapters/<run-id>/` |
| Documentation | `.md` | Root and subdirectories |

## What CANNOT Go Here

| Forbidden | Reason |
|-----------|--------|
| `.gguf` files | Too large, not needed until public release |
| `.bin` / `.pt` / `.pth` files | Raw PyTorch format, use `.safetensors` instead |
| Tokens / API keys | Security risk |
| Private data / PII | Privacy risk |
| Raw training logs | May contain sensitive info |
| Billing / cost info | Financial risk |

## Naming Convention

```
adapters/
  kimari4b-micro-sft-adapter-v0/     # First micro SFT
    adapter_config.json
    adapter_model.safetensors (Git LFS)
    manifest.json
training/
  results/
    hf_jobs_micro_sft_real_summary.json
eval/
  baselines/
    baseline_qwen2.5-1.5b.json
  comparisons/
    adapter_v0_vs_baseline.json
```

## Gate Policy

- **Gate remains BLOCKED** regardless of what's stored here
- Uploading artifacts here does NOT advance the gate
- Only manual review can advance the gate
- No automatic gate transitions

## Access Control

- Repository: `smouj/kimari-4b-artifacts`
- Visibility: **Private**
- Access: Smouj013 only
- No collaborator access without explicit approval

## Git LFS

`.gitattributes` tracks `*.safetensors` via Git LFS:

```
*.safetensors filter=lfs diff=lfs merge=lfs
```

This prevents large binary files from bloating the git history.

## Linking to Public Repo

The public repo (`smouj/kimari-local-ai`) can reference private artifacts via:
- Summary JSON files (sanitized, no weights)
- Documentation describing the artifacts
- Hash references for verification

**Never** link directly to private repo files from public documentation.