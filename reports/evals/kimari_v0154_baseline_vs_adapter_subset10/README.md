# KimariEval v0.1.54 — Baseline vs Adapter Subset10 Results

> **Status: COMPLETED** — Pipeline validation passed. Ready for subset30.

## Job Info

| Field | Value |
|-------|-------|
| **Job ID** | `6a03be047618f125ee2b7a5a` |
| **Status** | COMPLETED |
| **Flavor** | a10g-small |
| **Base model** | Qwen/Qwen2.5-1.5B-Instruct |
| **Adapter** | Smouj013/kimari4b-micro-sft-adapter-v0 (private) |
| **Dataset** | KimariEval Private v1 (subset 10) |
| **Temperature** | 0.2 |
| **Max tokens** | 256 |

## Results

| Metric | Baseline | Adapter |
|--------|----------|---------|
| **Completion rate** | 100% (10/10) | 100% (10/10) |
| **Errors** | 0 | 0 |
| **Avg response length** | 973.7 chars | 959.6 chars |
| **Adapter loaded** | N/A | ✅ Yes |

## Categories Covered

networking (1), python (3), style (1), agents (2), gguf (1), llama-cpp (1), linux (1)

## Key Findings

1. **Pipeline works**: Base model loads, runs eval, adapter loads from private repo, runs eval again
2. **No errors**: Both baseline and adapter completed all 10 items
3. **Similar lengths**: Baseline avg 973.7 vs adapter avg 959.6 chars
4. **No scoring**: score_status = not_scored (requires manual review)

## Decision

- **ready_for_subset30**: ✅ true
- Pipeline validated, adapter loads correctly, no errors

## Scope

This run is a private completion/integrity check only. It is not a public benchmark and does not include automatic scoring. Manual review is required before any gate decision.

## Safety

- `raw_outputs_committed`: false
- `public_benchmark_allowed`: false
- `manual_review_required`: true
- `gate_state`: BLOCKED
- No raw outputs committed to git
- No public benchmark claims