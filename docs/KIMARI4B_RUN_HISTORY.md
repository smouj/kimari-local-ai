# Kimari-4B Run History

> Chronological record of all Kimari-4B training and evaluation runs.

## Run 1: Micro SFT Smoke (Ephemeral)

| Field | Value |
|-------|-------|
| **Job ID** | `6a038ec87618f125ee2b7984` |
| **Type** | HF Jobs smoke test |
| **Base model** | Qwen2.5-1.5B |
| **Hardware** | A10G (small) |
| **Steps** | 10 |
| **Loss** | 2.62 → 3.19 |
| **Result** | ✅ Completed — adapter **not persisted** (ephemeral run) |
| **Docs** | `docs/KIMARI4B_MICRO_SFT_RESULT.md` |

> **Note**: This was a smoke test to validate the HF Jobs pipeline. The adapter was not saved to any repo and no weights were uploaded.

## Run 2: Micro SFT Persisted

| Field | Value |
|-------|-------|
| **Job ID** | `6a03a25e72518a06598ffae0` |
| **Type** | Micro SFT with adapter persistence |
| **Base model** | Qwen2.5-1.5B |
| **Hardware** | A10G (small) |
| **Adapter repo** | `Smouj013/kimari4b-micro-sft-adapter-v0` (private) |
| **Result** | ✅ Completed — adapter **persisted** to private repo |
| **Docs** | `docs/KIMARI4B_MICRO_SFT_PERSISTED_RESULT.md` |

> **Note**: This adapter is private. No public weights, GGUF, or benchmark claims. Gate remains BLOCKED.

## Evaluation: KimariEval Private v1

| Field | Value |
|-------|-------|
| **Type** | Private baseline vs adapter evaluation |
| **Cases** | 104 across 7 categories |
| **Subset10** | ✅ Completed — completion check passed |
| **Subset30** | ⏳ Pending — not yet run |
| **Docs** | `docs/KIMARI_EVAL_PRIVATE_V1.md` |

> **Note**: No raw evaluation outputs are committed. No public benchmark claims.

## Status

- **Gate**: 🔒 BLOCKED
- **Kimari-4B**: Not released. No public weights, adapters, or GGUF.
- **Next**: Subset30 evaluation (manual decision required before proceeding)