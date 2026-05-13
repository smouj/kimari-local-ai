# Kimari Runtime 1.5B SFT v1 — Evaluation Result

> ⚠️ **Status: BLOCKED** — Adapter not available for evaluation. The SFT v1 micro-run (Job `6a0501dae48bea4538b9c17a`) generated the adapter but did not persist it. Re-run with `--persist-adapter` required before evaluation can proceed.

## Objective

Compare the SFT v1 micro-run adapter (10 steps) against the base model (Qwen/Qwen2.5-1.5B-Instruct) using KimariEval subset10.

## Blocker

- **Adapter not persisted**: The micro-run generated an adapter on the HF Jobs container but did not save it to any repository
- **adapter_committed: false** in run summary
- **hf_public_upload_performed: false**
- **Resolution**: Re-run the micro-run with `--persist-adapter` to save to `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private)

## Evaluation Setup (Pending)

- **Subset**: 10 cases from KimariEval Private v1
- **Comparison**: baseline vs adapter
- **Metrics**: accuracy, exact_match, containment
- **Temperature**: 0.2
- **Max tokens**: 256

## Results

> Not yet executable. Blocked on adapter availability.

| Metric | Baseline | Adapter |
| --- | --- | --- |
| Load success | — | — |
| Generation success | — | — |
| Completion rate | — | — |

## Safety Assertions

- **score_status**: not_scored (blocked)
- **manual_review_required**: true
- **raw_outputs_committed**: false
- **public_benchmark_allowed**: false
- **gate_state**: BLOCKED

## Key Rules

1. No public benchmark claims
2. No raw outputs committed to git
3. No public weights, GGUF, or adapter
4. Gate remains BLOCKED
5. Adapter not persisted (must re-run with persist)
6. Manual review required before any decisions

## Decision

- **ready_for_subset30**: false (blocked on adapter availability)
- **next_step**: Re-run SFT v1 micro-run with `--persist-adapter` on HF Jobs