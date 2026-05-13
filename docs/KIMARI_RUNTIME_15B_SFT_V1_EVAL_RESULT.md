# Kimari Runtime 1.5B SFT v1 — Evaluation Result

> ⚠️ **Status: PENDING** — Infrastructure ready, evaluation not yet executed.

## Objective

Compare the SFT v1 micro-run adapter (10 steps) against the base model (Qwen/Qwen2.5-1.5B-Instruct) using KimariEval subset10.

## Base Model vs Adapter

| | Base Model | Adapter |
| --- | --- | --- |
| Model | Qwen/Qwen2.5-1.5B-Instruct | SFT v1 micro-run (10 steps) |
| Source | HuggingFace public | HF Jobs container (not persisted) |
| Load status | Pending | Pending |
| Generation | Pending | Pending |

## Evaluation Setup

- **Subset**: 10 cases from KimariEval Private v1
- **Comparison**: baseline vs adapter
- **Metrics**: accuracy, exact_match, containment
- **Temperature**: 0.2
- **Max tokens**: 256

## Results

> Not yet executed. Results will be populated after evaluation.

## Safety Assertions

- **score_status**: not_scored (pending manual review)
- **manual_review_required**: true
- **raw_outputs_committed**: false
- **public_benchmark_allowed**: false
- **gate_state**: BLOCKED

## Key Rules

1. No public benchmark claims
2. No raw outputs committed to git
3. No public weights, GGUF, or adapter
4. Gate remains BLOCKED
5. Adapter not persisted (micro-run only)
6. Manual review required before any decisions

## Decision

- **ready_for_subset30**: TBD (pending evaluation results)