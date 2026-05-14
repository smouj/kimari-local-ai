# Kimari Runtime 1.5B SFT v1 — Evaluation Plan

## Objective

Evaluate the SFT v1 adapter against the base model using KimariEval while keeping all results private and gate BLOCKED.

## Context

- **100-step full-run**: Job `6a052235e48bea4538b9c309`
- **Adapter status**: ✅ Persisted to `Smouj013/kimari-runtime-15b-sft-v1-adapter` (private)
- **This is NOT a final model** — it is a candidate adapter for validation
- **Gate**: 🔒 BLOCKED

## Evaluation Phases

### Phase 1: Eval Readiness (v0.1.64-alpha) ✅
- [x] SFT v1 run summary validated
- [x] Result doc completed
- [x] Eval config created
- [x] Eval readiness validator created
- [x] Eval infrastructure created

### Phase 1.5: Adapter Availability (v0.1.67-alpha) ✅
- [x] Adapter persisted to HF private repo
- [x] Adapter load checker created
- [x] Eval runner created

### Phase 2: Subset10 Evaluation (v0.1.68-alpha) ✅
- [x] Baseline evaluation: 10/10 items completed (100%)
- [x] Adapter evaluation: 10/10 items completed (100%)
- [x] Both models loaded and generated successfully

### Phase 3: 100-step Full-run (v0.1.69-alpha) ✅
- [x] Guarded `--full-run` enabled
- [x] 100-step training completed
- [x] Adapter persisted to private repo
- [x] Eval loss improved to 2.240 @ step100

### Phase 4: Subset30 Evaluation (v0.1.70-alpha) ✅
- [x] Eval job submitted to HF Jobs (`6a05236ee48bea4538b9c315`)
- [x] Baseline evaluation: 30/30 items completed (100%)
- [x] Adapter evaluation: 30/30 items completed (100%)
- [x] Both models loaded and generated successfully

### Phase 5: Scoring/Quality Evaluation (next)
- [ ] Capture raw outputs privately (do not commit)
- [ ] Implement sanitized scoring summary
- [ ] Compare baseline vs adapter quality against ideal answers
- [ ] Decide whether to run 500-step full-run

## Subset30 Results

| Metric | Baseline | Adapter |
| --- | --- | --- |
| Load success | ✅ | ✅ |
| Generation success | ✅ | ✅ |
| Completion rate | 30/30 (1.0) | 30/30 (1.0) |

- **Eval Job**: `6a05236ee48bea4538b9c315` on a10g-small
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

1. **No public benchmark** — all evaluation results are private/internal only.
2. **No raw outputs committed** — raw generations stay in private artifacts only.
3. **Manual review required** — no release decision from completion checks alone.
4. **Gate remains BLOCKED** — no public release of weights, GGUF, or benchmarks.

## Next Step

Build a scoring/quality eval before training longer or converting to GGUF.
