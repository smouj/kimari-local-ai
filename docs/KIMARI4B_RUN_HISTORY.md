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

## Run 4: SFT v1 Real Micro-Run

| Field | Value |
|-------|-------|
| **Job ID** | `6a0501dae48bea4538b9c17a` |
| **Run ID** | kimari-runtime-15b-sft-v1 |
| **Type** | SFT v1 micro-run (10 steps) |
| **Base model** | Qwen/Qwen2.5-1.5B-Instruct |
| **Hardware** | A10G (small) |
| **Steps** | 10 |
| **Loss** | 2.753 → 2.652 (eval) |
| **Accuracy** | 52.08% |
| **Result** | ✅ COMPLETED — adapter **not persisted** (micro-run) |
| **Artifact status** | Private adapter generated, not committed |
| **Public release status** | None |
| **Gate state** | 🔒 BLOCKED |
| **Docs** | `docs/KIMARI_RUNTIME_15B_SFT_V1_RESULT.md`, `docs/assets/results/sft_v1_run_summary.json` |

> **Note**: This was a micro-run (10 steps) to validate the SFT v1 pipeline. Not a final model. No public weights, GGUF, or benchmarks. Gate remains BLOCKED.

## Run 5: SFT v1 Eval Subset10 — BLOCKED

| Field | Value |
|-------|-------|
| **Run ID** | kimari-runtime-15b-sft-v1-eval-subset10 |
| **Type** | Baseline vs Adapter evaluation (subset10) |
| **Status** | 🔒 BLOCKED — Adapter not persisted |
| **Blocker** | SFT v1 micro-run did not persist adapter. Must re-run with --persist-adapter |
| **Result** | ❌ BLOCKED — cannot evaluate without adapter |
| **Docs** | `docs/KIMARI_RUNTIME_15B_SFT_V1_EVAL_RESULT.md` |

> **Note**: The SFT v1 micro-run (Run 4) generated the adapter on the HF Jobs container but did not save it. To evaluate, the micro-run must be re-executed with adapter persistence enabled.

## Run 6: SFT v1 Micro-Run with --persist-adapter

| Field | Value |
|-------|-------|
| **Job ID** | `6a05123b3308d79117b8f356` |
| **Run ID** | kimari-runtime-15b-sft-v1 |
| **Type** | SFT v1 micro-run (10 steps) with adapter persistence |
| **Base model** | Qwen/Qwen2.5-1.5B-Instruct |
| **Hardware** | A10G (small) |
| **Steps** | 10 |
| **Loss** | 2.753 → 2.652 (eval) |
| **Accuracy** | 52.08% |
| **Adapter repo** | `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private) |
| **Result** | ✅ COMPLETED — adapter **persisted** to Smouj013/kimari-runtime-15b-sft-v1-adapter (private) |
| **Gate state** | 🔒 BLOCKED |
| **Docs** | `docs/KIMARI_RUNTIME_15B_SFT_V1_RESULT.md` |

> **Note**: Re-run of the SFT v1 micro-run with `--persist-adapter` flag to save the adapter to a private HuggingFace repo. If upload succeeds, enables eval subset10.

## Status

- **Gate**: 🔒 BLOCKED
- **Kimari-4B**: Not released. No public weights, adapters, or GGUF.
- **Next**: If adapter upload succeeds → eval subset10 → subset30