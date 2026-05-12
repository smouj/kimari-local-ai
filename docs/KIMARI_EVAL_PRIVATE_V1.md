# KimariEval Private v1

> Private evaluation dataset for Kimari-4B baseline and adapter comparison.

## Purpose

KimariEval Private v1 measures model performance on tasks relevant to Kimari's target use cases: Spanish technical support, coding/debugging, server operations, local LLM/GGUF operations, AI agent behavior, refusal/safety, and style consistency.

## What This Evaluates

| Category | Focus | Items |
|----------|-------|-------|
| spanish_technical | Spanish-language technical support | 16 |
| coding_debug | Programming, debugging, best practices | 14 |
| server_ops | Linux server administration | 15 |
| local_llm_gguf | Local LLM deployment, GGUF, quantization | 14 |
| openclaw_agents | AI agent behavior, tools, safety | 14 |
| refusal_safety | Appropriate refusals, honest benchmarks | 15 |
| style_consistency | Response quality, clarity, consistency | 15 |
| **Total** | | **100** |

## What This Does NOT Evaluate

- **Public benchmarks** (MMLU, HumanEval, etc.) — this is a private eval
- **Model quality claims** — scores are `not_scored` until manual review
- **Production readiness** — this is evaluation only
- **Benchmark contamination** — all items are original, not from public benchmarks

## Dataset Format

Each item is a JSON object:

```json
{
  "id": "es-tech-001",
  "prompt": "¿Cómo configuro un servidor DNS caching en Linux?",
  "ideal": "Usa dnsmasq o systemd-resolved como caching DNS...",
  "tags": ["dns", "linux", "networking", "spanish"],
  "difficulty": "medium"
}
```

## Running

```bash
# Dry-run (no model calls)
python eval/scripts/run_kimari_eval.py \
    --model-label qwen25-15b-base \
    --dataset-dir eval/kimari_private_v1 \
    --dry-run --json

# With endpoint
python eval/scripts/run_kimari_eval.py \
    --model-label qwen25-15b-base \
    --dataset-dir eval/kimari_private_v1 \
    --endpoint http://127.0.0.1:8080/v1 \
    --output-json reports/evals/baseline.json \
    --json
```

## Validation

```bash
python eval/scripts/validate_kimari_eval.py --dataset-dir eval/kimari_private_v1 --json
```

## Scoring

All results have `score_status: "not_scored"` and `manual_review_required: true`. Automatic scoring is not implemented — this would require a judge model or manual evaluation.

**No benchmark claims** should be made from this dataset. Results are for internal development only.

## Gate

**BLOCKED** — This eval is private. No public benchmark claims.