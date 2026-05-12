# KimariEval Baseline vs Adapter Run Guide

> How to run baseline vs adapter evaluation using KimariEval Private v1.

## Objective

Compare Qwen2.5-1.5B-Instruct (base) against Kimari-4B micro-SFT adapter (private) on the same eval set, using identical generation parameters.

## Prerequisites

- HF Jobs access confirmed (`hf jobs list` works)
- Eval config: `eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml`
- Eval dataset: `eval/kimari_private_v1/` (104 items across 7 categories)
- Adapter: `Smouj013/kimari4b-micro-sft-adapter-v0` (private HF repo)

## Running

### Step 1: Dry-run (recommended first)

```bash
python eval/scripts/hf_jobs_run_kimari_eval.py \
    --config eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml \
    --dry-run --json
```

This generates a plan without submitting anything. Check:
- `subset_size` is reasonable (30 for first run)
- `estimated_cost_usd` is within budget
- Safety flags are correct

### Step 2: Print command

```bash
python eval/scripts/hf_jobs_run_kimari_eval.py \
    --config eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml \
    --print-command
```

Review the command before submitting.

### Step 3: Submit (requires explicit confirmation)

```bash
python eval/scripts/hf_jobs_run_kimari_eval.py \
    --config eval/configs/kimari_eval_v1_baseline_vs_adapter.yaml \
    --require-jobs-access \
    --allow-submit \
    --yes
```

**Important**: This actually submits a HF Job. Cost estimate: ~$1-2 for 30 items (2 models × 30 prompts).

### Step 4: Check results

After the job completes, capture the summary JSON. No raw outputs are committed.

### Step 5: Compare runs (after both baseline and adapter)

```bash
python eval/scripts/compare_kimari_eval_runs.py \
    --baseline-summary reports/evals/baseline_summary.json \
    --adapter-summary reports/evals/adapter_summary.json \
    --output-md reports/evals/comparison.md \
    --output-json reports/evals/comparison.json
```

## Subset Strategy

1. **First run**: `subset_size: 30` (validate pipeline, ~$1-2)
2. **Second run**: `subset_size: 104` (full eval, ~$3-5)
3. **Any issues**: Fix pipeline, then re-run

## Generation Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| temperature | 0.2 | Low for reproducibility |
| max_tokens | 384 | Sufficient for detailed answers |
| top_p | 0.9 | Standard nucleus sampling |
| seed | 42 | Reproducible subset selection |

## Safety

- **No raw outputs committed** to git
- **No benchmark claims** made from results
- **No public upload** of eval data or results
- **Gate**: BLOCKED until manual review
- **manual_review_required**: true
- **public_benchmark_allowed**: false

## What Gets Committed

- Eval config (YAML)
- Eval runner scripts
- Summary templates
- **Pending** result placeholders (status: pending, no actual data)
- **NOT**: raw model outputs, generation text, benchmark scores

## Gate

**BLOCKED** — No benchmark claims. Results are for internal development only.