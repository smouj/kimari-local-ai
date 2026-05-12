# Kimari-4B Private Adapter Repository

> Policy for the `Smouj013/kimari4b-micro-sft-adapter-v0` private model repository on Hugging Face.

## Purpose

This private HF model repository stores LoRA adapter weights generated during Kimari-4B micro SFT training runs. It is **private** and accessible only to the Smouj013 account.

## Repository Details

| Field | Value |
|-------|-------|
| **Repo ID** | `Smouj013/kimari4b-micro-sft-adapter-v0` |
| **Type** | Hugging Face Model Repository |
| **Visibility** | **Private** |
| **Owner** | Smouj013 |
| **LFS** | Enabled for `*.safetensors` |

## What CAN Go Here

| Artifact | Format | Description |
|----------|--------|-------------|
| LoRA adapter weights | `adapter_model.safetensors` | The trained LoRA weights |
| Adapter config | `adapter_config.json` | LoRA configuration (r, alpha, target_modules) |
| Tokenizer files | `tokenizer.json`, `tokenizer_config.json` | If saved alongside adapter |
| Manifest | `manifest.json` | Sanitized summary (no tokens, no private paths) |
| README | `README.md` | Must state: private, no public release, gate BLOCKED |

## What CANNOT Go Here

| Forbidden | Reason |
|-----------|--------|
| Full model weights | Too large, not needed for LoRA |
| `.bin` / `.pt` / `.pth` files | Use `.safetensors` instead |
| GGUF files | Not needed until public release |
| Tokens / API keys | Security risk |
| Raw training logs | May contain sensitive info |
| Billing / cost data | Financial risk |
| Public release claims | Gate is BLOCKED |

## README Requirements

The README in this private repo MUST include:

1. **Private notice**: "This repository is private and contains adapter weights for internal evaluation only."
2. **No public release**: "No public release of Kimari-4B weights is planned at this time."
3. **Gate status**: "Gate: BLOCKED"
4. **Base model**: Reference to `Qwen/Qwen2.5-1.5B-Instruct` (Apache 2.0)
5. **Training details**: Dataset, steps, date (sanitized)
6. **No download instructions**: Do not provide public download commands

## Access Control

- **Visibility**: Private (Smouj013 only)
- **No collaborator access** without explicit approval
- **No public linking** from the `smouj/kimari-local-ai` repository
- **Public docs** only state: "Adapter persisted privately for internal evaluation. No public weights are available."

## Upload Process

The training runner (`hf_jobs_micro_sft_persisted.py`) handles upload:

1. After training, adapter is saved to `/tmp/kimari4b-micro-sft-adapter`
2. Runner calls `huggingface_hub.HfApi.upload_folder()` to push to the private repo
3. Only `adapter_model.safetensors` and `adapter_config.json` are uploaded
4. No raw logs, no tokens, no billing data

## Gate Policy

- **Gate remains BLOCKED** regardless of what's stored here
- Uploading to this private repo does NOT advance the gate
- Only manual review can advance the gate
- No automatic gate transitions

## Naming Convention

```
Smouj013/kimari4b-micro-sft-adapter-v0    # First persisted adapter (v0.1.51)
Smouj013/kimari4b-micro-sft-adapter-v1    # Second run (if needed)
Smouj013/kimari4b-eval-adapter-v0          # Evaluation adapter (future)
```