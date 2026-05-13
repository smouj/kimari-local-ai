# Kimari Runtime 1.5B SFT v1 — Evaluation Plan

## Objective

Evaluate the SFT v1 micro-run adapter (10 steps, QLoRA, Qwen2.5-1.5B-Instruct) against the base model using KimariEval.

## Context

- **SFT v1 micro-run**: Job `6a0501dae48bea4538b9c17a` (10 steps, loss 2.753→2.652 eval)
- **Adapter status**: Generated but NOT persisted to HuggingFace
- **This is NOT a final model** — it is a pipeline validation micro-run
- **Gate**: 🔒 BLOCKED

## Evaluation Phases

### Phase 1: Eval Readiness (v0.1.64-alpha)
- [x] SFT v1 run summary validated
- [x] Result doc COMPLETED
- [x] Eval subset10 config created
- [x] Eval readiness validator created
- [ ] Adapter load check (local)
- [ ] Generation check (local)

### Phase 2: Subset10 Evaluation (v0.1.65-alpha)
- Run KimariEval subset10: base vs adapter
- Compare accuracy, exact_match, containment
- Manual review of outputs
- **No public benchmark claims**

### Phase 3: Subset30 Evaluation (v0.1.66-alpha, if subset10 passes)
- Run KimariEval subset30: base vs adapter
- Full manual review
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
5. **Adapter not persisted** — The micro-run adapter was generated but not saved to HF

## Adapter Access

The SFT v1 micro-run adapter was generated on HF Jobs container `6a0501dae48bea4538b9c17a` but was NOT persisted to a HuggingFace repo. For evaluation:

- If adapter files are available locally from a previous download, use those
- If not available, the adapter must be re-generated via a new micro-run with `--persist-adapter` flag
- The adapter path in eval config points to `training/output/kimari-runtime-15b-sft-v1/adapter`

## Next Step

If eval readiness validation passes (v0.1.64), proceed to subset10 evaluation (v0.1.65).