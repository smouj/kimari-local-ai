# Open Base Bakeoff v1 — Reports

> Status: **Pending** — No evaluation has been executed yet.
> Gate: **BLOCKED** — No public benchmark claims.

## Directory Structure

```
open_base_bakeoff_v1/
├── README.md                    — This file
├── summary.pending.json         — Pending summary (no results yet)
├── qwen25_15b.summary.json       — Qwen2.5-1.5B results (pending)
├── smollm2_17b.summary.json      — SmolLM2-1.7B results (pending)
├── smollm3_3b.summary.json       — SmolLM3-3B results (pending)
└── qwen3_4b.summary.json         — Qwen3-4B results (pending)
```

## Safety Constraints

- **No raw outputs committed** — raw model responses are not stored in git
- **No public benchmark claims** — results are for internal review only
- **Manual review required** — all results require human evaluation
- **Gate BLOCKED** — no model release decisions until review complete
- **Only permissive-license bases** — Apache 2.0, MIT, BSD

## Phases

1. **Smoke** (5 prompts, all 4 candidates) — Quick validation
2. **Subset10** (10 prompts, all 4 candidates) — Initial comparison
3. **Subset30** (30 prompts, top 2 candidates) — Deeper evaluation

## Candidates

| ID | Model | License | Size | Role |
|----|-------|---------|------|------|
| qwen25-15b | Qwen/Qwen2.5-1.5B-Instruct | Apache 2.0 | 1.5B | Runtime |
| smollm2-17b | HuggingFaceTB/SmolLM2-1.7B-Instruct | Apache 2.0 | 1.7B | Runtime alt |
| smollm3-3b | HuggingFaceTB/SmolLM3-3B | Apache 2.0 | 3B | Core |
| qwen3-4b | Qwen/Qwen3-4B-Instruct-2507 | Apache 2.0 | 4B | 4B candidate |

## Blocked (Not Evaluated)

| Model | License | Reason |
|-------|---------|--------|
| Qwen/Qwen2.5-3B-Instruct | qwen-research | Research-only |
| google/gemma-3-4b-it | Gemma | Custom restrictive |

---

_This bakeoff is internal. No results will be published as public benchmarks._