# Baseline Qwen2.5-1.5B-Instruct — Evaluation Plan

> Plan for evaluating the base model before adapter comparison.

## Model

- **Base model**: Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0)
- **Parameters**: 1.5B
- **Quantization**: Q4_K_M (for GTX 1060 6GB compatibility)

## Status

**PENDING** — Baseline evaluation has not been run yet.

This plan exists to prepare the evaluation infrastructure. No results are claimed.

## Dataset

- **KimariEval Private v1**: 100 items across 7 categories
- **Categories**: spanish_technical (16), coding_debug (14), server_ops (15), local_llm_gguf (14), openclaw_agents (14), refusal_safety (15), style_consistency (15)
- **Difficulty**: easy (28), medium (48), hard (24)

## Plan

```json
{
  "model_label": "qwen25-15b-base",
  "model_source": "Qwen/Qwen2.5-1.5B-Instruct",
  "dataset": "kimari_private_v1",
  "total_items": 100,
  "temperature": 0.1,
  "max_tokens": 512,
  "seed": 42,
  "status": "pending",
  "manual_review_required": true,
  "no_benchmark_claim": true,
  "notes": "Baseline evaluation pending. No results yet."
}
```

## How to Run

```bash
# Dry-run first
python eval/scripts/run_kimari_eval.py \
    --model-label qwen25-15b-base \
    --dataset-dir eval/kimari_private_v1 \
    --dry-run --json

# With local endpoint (after starting llama-server)
python eval/scripts/run_kimari_eval.py \
    --model-label qwen25-15b-base \
    --dataset-dir eval/kimari_private_v1 \
    --endpoint http://127.0.0.1:8080/v1 \
    --output-json reports/evals/baseline_qwen25_15b/baseline_results.json \
    --output-md reports/evals/baseline_qwen25_15b/baseline_report.md \
    --json
```

## Gate

**BLOCKED** — No results, no benchmark claims.