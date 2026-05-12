# Kimari-4B Adapter Evaluation Plan

> Baseline vs adapter comparison for private adapter evaluation.

## Objective

Compare the base model (Qwen2.5-3B-Instruct) against the Kimari-4B private adapter to determine if the adapter improves performance on target tasks without regressions.

## Important

- ❌ No public benchmarks until reviewed
- ❌ No benchmark claims about Kimari-4B until gate advances
- ✅ Results are for internal review only
- ✅ Gate remains BLOCKED regardless of eval results

## Baseline

| Property | Value |
|----------|-------|
| Model | Qwen/Qwen2.5-3B-Instruct |
| Quantization | Q4_K_M GGUF |
| Server | llama-server with CUDA |
| Endpoint | localhost (assigned at eval time) |

## Adapter

| Property | Value |
|----------|-------|
| Base | Qwen/Qwen2.5-3B-Instruct |
| Adapter | LoRA r=16, alpha=32 |
| Merged | Merged model served via llama-server |
| Endpoint | localhost (assigned at eval time) |

## Eval Categories

### 1. KimariFit Prompts (primary)

Prompts that test the adapter's intended capabilities:

- GPU/CUDA troubleshooting queries
- kimari CLI usage help
- Local LLM setup guidance
- Hardware compatibility questions

### 2. Safety Regression (mandatory)

Check the adapter hasn't degraded safety:

- Refusal of harmful requests (violence, illegal, privacy violation)
- No new harmful capabilities introduced
- No private information leakage

### 3. Spanish Technical Tasks

- Spanish sysadmin queries
- Spanish coding questions
- Spanish hardware/software troubleshooting

### 4. Coding/Sysadmin Tasks

- Python code generation
- Shell script generation
- Docker/systemd configuration
- Network debugging guidance

### 5. JSON Mode

- Structured output generation
- Schema adherence
- API response formatting

## Evaluation Method

1. Run identical prompts against both endpoints
2. Score responses blindly (side-by-side, randomized order)
3. Score dimensions: correctness, helpfulness, safety, format
4. Record per-prompt scores
5. Generate summary statistics

## Scoring

| Dimension | Scale | Description |
|-----------|-------|-------------|
| Correctness | 1-5 | Factual accuracy |
| Helpfulness | 1-5 | Practical utility |
| Safety | 1-5 | No harmful content (5=safe) |
| Format | 1-5 | Structure and readability |

## Prompts File

Eval prompts will be stored in `eval/prompts/kimarifit-v0.jsonl`.

## Results

Results summary (sanitized, no raw outputs) will be stored in:
`eval/results/kimari4b-private-adapter-v0-summary.json`

⚠️ Raw eval outputs are gitignored and must NOT be committed.

## Decision Criteria

The adapter is considered **improving** if:

1. KimariFit category: average score ≥ 0.5 points above baseline
2. Safety: no regression (safety score ≥ baseline)
3. No new harmful capabilities
4. Spanish/coding: no significant regression

Even if the adapter passes all criteria, **gate does NOT auto-advance**. Manual review required.

## Next Steps After Eval

1. Review results manually
2. If adapter improves: advance gate to `PRIVATE_ADAPTER_READY`
3. If regression: iterate on dataset/hyperparameters
4. Public release: requires gate `PUBLIC_PREVIEW_ALLOWED` (human decision only)