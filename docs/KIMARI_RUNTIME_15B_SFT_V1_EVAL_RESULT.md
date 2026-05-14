# Kimari Runtime 1.5B SFT v1 — Evaluation Result

> ⚠️ **Status: READY FOR EVALUATION** — Adapter persisted to `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private). Evaluation subset10 can now proceed.

## Objective

Compare the SFT v1 micro-run adapter (10 steps) against the base model (Qwen/Qwen2.5-1.5B-Instruct) using KimariEval subset10.

## Blocker

- **Adapter persisted**: v0.1.67-alpha re-ran micro-run with `--persist-adapter` — adapter uploaded to `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private repo)
- **Job**: `6a0512bd3308d79117b8f367` (with `--secrets HF_TOKEN`)
- **adapter_model.safetensors**: 8.73 MB
- **Ready for subset10 evaluation**

## Evaluation Setup (Pending)

- **Subset**: 10 cases from KimariEval Private v1
- **Comparison**: baseline vs adapter
- **Metrics**: accuracy, exact_match, containment
- **Temperature**: 0.2
- **Max tokens**: 256

## Results

> Evaluation now executable. Adapter is available at Smouj013/kimari-runtime-15b-sft-v1-adapter (private).

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