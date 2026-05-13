# KimariEval v0.1.54 Result

> Baseline vs adapter evaluation (subset10) on HF Jobs — COMPLETED ✅

## Job Details

- **Job ID**: `6a03be047618f125ee2b7a5a`
- **Status**: COMPLETED
- **Base model**: Qwen/Qwen2.5-1.5B-Instruct
- **Adapter**: Smouj013/kimari4b-micro-sft-adapter-v0 (private)
- **Subset size**: 10
- **Temperature**: 0.2, **Max tokens**: 256

## Results Summary

| Metric | Baseline | Adapter |
|--------|----------|---------|
| Completion rate | 100% (10/10) | 100% (10/10) |
| Errors | 0 | 0 |
| Avg response length | 973.7 | 959.6 |
| Adapter loaded | N/A | ✅ |

## Adapter Load Status

✅ Adapter loaded successfully from private repo `Smouj013/kimari4b-micro-sft-adapter-v0`.

No permission errors. No download failures. LoRA merged correctly.

## Decision

- **ready_for_subset30**: true ✅
- Pipeline validated end-to-end
- No errors in either baseline or adapter runs
- Next step: subset30 evaluation

## No Benchmark Claims

This is a private evaluation for internal development. No public benchmark scores. No comparison claims. Gate BLOCKED.

## Scope

This run is a private completion/integrity check only. It is not a public benchmark and does not include automatic scoring. Manual review is required before any gate decision.

## Safety

- No raw outputs committed
- No public benchmark claims
- No public weights/adapters/GGUF
- Gate: BLOCKED