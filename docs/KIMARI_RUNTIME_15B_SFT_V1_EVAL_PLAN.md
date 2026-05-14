# Kimari Runtime 1.5B SFT v1 — Evaluation Plan

## Objective

Evaluate the SFT v1 micro-run adapter (10 steps, QLoRA, Qwen2.5-1.5B-Instruct) against the base model using KimariEval.

## Context

- **SFT v1 micro-run**: Job `6a0512bd3308d79117b8f367` (10 steps, loss 2.753→2.653 eval)
- **Adapter status**: ✅ Persisted to Smouj013/kimari-runtime-15b-sft-v1-adapter (private)
- **This is NOT a final model** — it is a pipeline validation micro-run
- **Gate**: 🔒 BLOCKED

## Evaluation Phases

### Phase 1: Eval Readiness (v0.1.64-alpha) ✅
- [x] SFT v1 run summary validated
- [x] Result doc COMPLETED
- [x] Eval subset10 config created
- [x] Eval readiness validator created
- [x] Eval infrastructure created (v0.1.65)

### Phase 1.5: Adapter Availability (v0.1.67-alpha) ✅ COMPLETED
- [x] Adapter persisted to HF private repo (Smouj013/kimari-runtime-15b-sft-v1-adapter)
- [x] Adapter load checker created (dry-run passes)
- [x] Eval runner created (dry-run passes)
- ✅ **Resolved**: SFT v1 micro-run re-run with `--persist-adapter` — adapter uploaded successfully

### Phase 2: Subset10 Evaluation (v0.1.68-alpha) ✅ COMPLETED
- [x] Re-run SFT v1 micro-run with --persist-adapter (v0.1.67-alpha ✅)
- [x] Eval job submitted to HF Jobs (6a051807e48bea4538b9c29d)
- [x] Baseline evaluation: 10/10 items completed (100%)
- [x] Adapter evaluation: 10/10 items completed (100%)
- [x] Both models loaded and generated successfully
- ✅ **Ready for subset30**: completion_rate = 1.0 ≥ 0.8

### Phase 3: Subset30 Evaluation (v0.1.69-alpha, next)
- Run KimariEval subset30: base vs adapter
- Full manual review
- **No public benchmark claims**

## Subset10 Results

| Metric | Baseline | Adapter |
| --- | --- | --- |
| Load success | ✅ | ✅ |
| Generation success | ✅ | ✅ |
| Completion rate | 10/10 (1.0) | 10/10 (1.0) |

- **Eval Job**: `6a051807e48bea4538b9c29d` on a10g-small
- **Temperature**: 0.2, **Max tokens**: 256, **Top-p**: 0.9
- **score_status**: not_scored (completion check only)
- **No public benchmark claims**

## Safety Constraints

| Constraint | Value |
| --- | --- |
| public_benchmark_allowed | false |
| raw_outputs_commit_allowed | false |
| manual_review_required | true |
| gate_state | BLOCKED |

## Key Rules

1. **No public benchmark** — All evaluation results are private, internal-only
2. **No raw outputs committed** — Evaluation outputs stay local
3. **Manual review required** — Every evaluation must be manually reviewed before any decision
4. **Gate remains BLOCKED** — No public release of weights, GGUF, or benchmarks

## Next Step

Proceed to subset30 evaluation (v0.1.69-alpha).