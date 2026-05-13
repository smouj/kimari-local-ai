# Kimari Runtime 1.5B SFT v1 — Subset10 Eval Report

> ⚠️ **Status: PENDING** — Evaluation has not been executed yet. This report contains infrastructure readiness only.

## Objective

Evaluate the SFT v1 micro-run adapter (10 steps, QLoRA, Qwen2.5-1.5B-Instruct) against the base model using KimariEval subset10.

## Context

- **SFT v1 micro-run**: Job `6a0501dae48bea4538b9c17a` (10 steps, loss 2.753→2.652 eval)
- **Adapter**: Generated but NOT persisted to HuggingFace
- **This is NOT a final model** — pipeline validation micro-run
- **Gate**: 🔒 BLOCKED

## Evaluation Config

| Parameter | Value |
| --- | --- |
| Base model | Qwen/Qwen2.5-1.5B-Instruct |
| Adapter | SFT v1 micro-run (10 steps) |
| Dataset | KimariEval Private v1 |
| Subset size | 10 |
| Comparison mode | baseline_vs_adapter |
| Temperature | 0.2 |
| Max tokens | 256 |

## Results

| Metric | Baseline | Adapter |
| --- | --- | --- |
| Load success | — | — |
| Generation success | — | — |
| Completion rate | — | — |
| Generation errors | — | — |

> Results will be populated after evaluation is executed.

## Safety

| Check | Value |
| --- | --- |
| score_status | not_scored |
| manual_review_required | true |
| raw_outputs_committed | false |
| public_benchmark_allowed | false |
| gate_state | BLOCKED |

## Key Assertions

- No public benchmark claims
- No raw outputs committed to git
- No public weights/GGUF/adapter
- Gate remains BLOCKED
- Adapter not persisted (micro-run only)
- manual_review_required=true

## Next Step

If eval readiness passes and load check succeeds, proceed to subset10 evaluation.