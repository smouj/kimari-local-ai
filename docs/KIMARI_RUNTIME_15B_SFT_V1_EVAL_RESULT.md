# Kimari Runtime 1.5B SFT v1 — Evaluation Result

> ✅ **Status: SUBSET30 COMPLETED** — Baseline vs 100-step adapter completion evaluation completed on HF Jobs. Both models achieved 100% completion rate on 30-item subset.

## Objective

Compare the SFT v1 100-step full-run adapter against the base model (Qwen/Qwen2.5-1.5B-Instruct) using KimariEval Private v1 subset30.

## Training Source

| Field | Value |
| --- | --- |
| Adapter training job | `6a052235e48bea4538b9c309` |
| Training mode | guarded `--full-run` |
| Steps | 100 |
| Eval loss @ step100 | 2.240 |
| Adapter repo | `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private) |

## Eval Job

| Field | Value |
| --- | --- |
| Eval job ID | `6a05236ee48bea4538b9c315` |
| Hardware | A10G small |
| Method | HF Jobs `uv run` with PEP 723 inline script |
| Subset size | 30 |
| Temperature | 0.2 |
| Max new tokens | 256 |
| Top-p | 0.9 |

## Results

| Metric | Baseline | Adapter |
| --- | --- | --- |
| Load success | ✅ Yes | ✅ Yes |
| Generation success | ✅ Yes | ✅ Yes |
| Completion rate | 30/30 (1.0) | 30/30 (1.0) |
| Completed items | 30 | 30 |
| Total items | 30 | 30 |

### Key Findings

- **Both models loaded successfully** on A10G with CUDA.
- **Both models generated outputs** for all 30 eval items.
- **100% completion rate** for both baseline and adapter.
- Adapter loaded from private repo `Smouj013/kimari-runtime-15b-sft-v1-adapter`.
- No generation errors for either model.

## Safety Assertions

- **score_status**: not_scored (requires judge model or manual review)
- **manual_review_required**: true
- **raw_outputs_committed**: false
- **public_benchmark_allowed**: false
- **gate_state**: BLOCKED

## Decision

- **ready_for_scoring_eval**: ✅ true
- **ready_for_500_step_run**: ✅ true, but scoring eval is recommended first
- **next_step**: Add quality/scoring eval before training longer or converting to GGUF
- **No accuracy/scoring claims**: This evaluation only verifies generation completion, not quality

## Evaluation Phases Completed

- [x] Phase 1: Eval Readiness (v0.1.64)
- [x] Phase 1.5: Adapter Availability (v0.1.67)
- [x] Phase 2: Subset10 Evaluation (v0.1.68)
- [x] Phase 3: 100-step Full-run Training (v0.1.69)
- [x] Phase 4: Subset30 Evaluation (v0.1.70)
- [ ] Phase 5: Scoring/quality evaluation

## No Release Claim

This is **not** a public model release. No public weights, GGUF, raw outputs, or benchmark claims are allowed yet.
