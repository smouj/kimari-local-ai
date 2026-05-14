# Hugging Face Deployment Status

> **Last reviewed: 2026-05-13** — Kimari Local AI public presence on Hugging Face.

## Current State

| Field | Value |
|-------|-------|
| **Repo version** | v0.1.71-alpha |
| **HF org card version** | v0.1.71-alpha |
| **Space version** | v0.1.71-alpha |
| **Gate** | BLOCKED |
| **Kimari-4B** | NOT released |

## Deployed Resources

| Resource | URL | Status |
|----------|-----|--------|
| **Space** | https://huggingface.co/spaces/kimari-ai/kimari-fit-lab | ✅ RUNNING |
| **Organization Card** | https://huggingface.co/spaces/kimari-ai/README | ✅ Updated |
| **Collection** | https://huggingface.co/collections/Smouj013/kimari-compatible-gguf-models-6a0352c75d2bfeff34d51e66 | ✅ 5 reference/community models |

## Space Details

- **Name**: `kimari-ai/kimari-fit-lab`
- **SDK**: Gradio 5.34.2
- **Visibility**: Public
- **Hardware**: CPU basic (free tier)
- **Function**: GPU compatibility checker — does **not** run any model

### What the Space Does

1. Shows GPU compatibility lookup table (GTX 1060, GTX 1080, RTX 2060, etc.)
2. Recommends Kimari profiles based on VRAM
3. Displays recommended CLI commands
4. Shows model compatibility table

### What the Space Does NOT Do

❌ Does not run any model
❌ Does not download any model
❌ Does not use any API keys
❌ Does not claim Kimari-4B is released
❌ Does not reveal billing/plan information

## Organization Card

The `kimari-ai` organization card at `kimari-ai/README` includes:

- Framework version: v0.1.71-alpha
- Kimari-4B: Not released yet
- GTX 1060 validation: Completed
- HF Jobs smoke: Completed
- Micro SFT: Completed (private)
- Private adapter: Persisted (private repo)
- KimariEval Private v1: Created (104 cases)
- Gate: BLOCKED

## Collection

The `kimari-compatible-gguf-models` collection contains 5 reference/community GGUF models that Kimari can help run locally.

**Important**: These are NOT official Kimari models. They are community/reference models curated by Smouj013 for the Kimari project.

### Collection Criteria

- Small to medium size (1B-8B parameters)
- GGUF format
- Reasonable for 6-8GB VRAM
- Clear license
- No false claims about being "official Kimari models"

## What Was NOT Uploaded

- ❌ No weights, adapters, or GGUF files
- ❌ No training checkpoints
- ❌ No raw logs
- ❌ No Kimari-4B model files (not yet created)
- ❌ No API keys, tokens, or billing information
- ❌ No benchmark results
- ❌ No eval raw outputs

## Gate Status

**BLOCKED** — Kimari is in alpha. No public model releases.

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-13 | v0.1.63-alpha | SFT v1 first real short run, gate BLOCKED |
| 2026-05-14 | v0.1.71-alpha | SFT v1 eval subset10 infrastructure, gate BLOCKED | | |
| 2026-05-12 | v0.1.45-alpha | Initial HF deployment (Space, Org Card, Collection) |

## Last Updated

2026-05-13