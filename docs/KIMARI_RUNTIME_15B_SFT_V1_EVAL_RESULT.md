# Kimari Runtime 1.5B SFT v1 — Evaluation Result

> ✅ **Status: COMPLETED** — Baseline vs adapter evaluation completed on HF Jobs. Both models achieved 100% completion rate on 10-item subset.

## Objective

Compare the SFT v1 micro-run adapter (10 steps) against the base model (Qwen/Qwen2.5-1.5B-Instruct) using KimariEval subset10.

## Eval Job

- **Job ID**: `6a051807e48bea4538b9c29d`
- **Hardware**: A10G (small)
- **Method**: HF Jobs `uv run` with PEP 723 inline script
- **Adapter**: `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private)
- **Previous failed job**: `6a05163be48bea4538b9c287` (seed parameter bug)

## Results

| Metric | Baseline | Adapter |
| --- | --- | --- |
| Load success | ✅ Yes | ✅ Yes |
| Generation success | ✅ Yes | ✅ Yes |
| Completion rate | 10/10 (1.0) | 10/10 (1.0) |
| Completed items | 10 | 10 |
| Total items | 10 | 10 |

### Key Findings

- **Both models loaded successfully** on A10G with CUDA
- **Both models generated outputs** for all 10 eval items
- **100% completion rate** for both baseline and adapter
- Adapter loaded from private repo `Smouj013/kimari-runtime-15b-sft-v1-adapter`
- No generation errors for either model

### Generation Parameters

| Parameter | Value |
| --- | --- |
| Temperature | 0.2 |
| Max new tokens | 256 |
| Top-p | 0.9 |
| Do sample | true |

## Safety Assertions

- **score_status**: not_scored (requires judge model or manual review)
- **manual_review_required**: true
- **raw_outputs_committed**: false
- **public_benchmark_allowed**: false
- **gate_state**: BLOCKED

## Key Rules

1. No public benchmark claims
2. No raw outputs committed to git
3. No public weights, GGUF, or adapter
4. Gate remains BLOCKED
5. Manual review required before any decisions

## Decision

- **ready_for_subset30**: ✅ true (completion rate ≥ 0.8)
- **next_step**: Proceed to subset30 evaluation (v0.1.69-alpha)
- **No accuracy/scoring claims**: This evaluation only verifies generation completion, not quality

## Evaluation Phases Completed

- [x] Phase 1: Eval Readiness (v0.1.64)
- [x] Phase 1.5: Adapter Availability (v0.1.67)
- [x] Phase 2: Subset10 Evaluation (v0.1.68) ✅ COMPLETED
- [ ] Phase 3: Subset30 Evaluation (v0.1.69+)