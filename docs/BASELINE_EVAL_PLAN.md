# Baseline Evaluation Plan — SmolLM3-3B Before SFT

> **Document Type:** Baseline evaluation plan  
> **Version:** v0.1.20-alpha  
> **Date:** 2026-05-22  
> **Status:** Active — baseline results are required BEFORE SFT to compare against the adapter

---

## Objective

Evaluate the base SmolLM3-3B model **without any fine-tuning** to establish a performance baseline. This baseline is essential for measuring the impact of supervised fine-tuning (SFT) and preference tuning (ORPO) in subsequent stages.

**No fine-tuned adapter exists yet.** This plan measures the raw, unmodified SmolLM3-3B model against the KimariFit evaluation suite so that every future adapter result can be compared against a known starting point.

---

## Why a Baseline Is Required

Without a baseline evaluation, there is no way to determine whether fine-tuning improved, degraded, or had no effect on model output quality. Specifically:

1. **Regression detection** — SFT may improve coding accuracy but degrade safety refusals. A baseline makes this detectable.
2. **Category-level comparison** — Some categories (e.g., Spanish technical) may need targeted improvement; the baseline reveals where.
3. **Decision gate** — Baseline results inform whether to proceed with ORPO after SFT, or whether a different approach is needed.
4. **Honest reporting** — Any future claims about adapter improvements must reference actual baseline numbers, not assumptions about base model capability.

---

## Model Under Evaluation

| Field | Value |
|-------|-------|
| **Model ID** | `HuggingFaceTB/SmolLM3-3B` |
| **Parameters** | ~3B |
| **License** | Apache 2.0 |
| **Context Length** | 16,384 tokens |
| **Quantization for Eval** | Q4_K_M (primary), Q5_K_M (secondary) |
| **Expected VRAM (Q4_K_M)** | ~2.2 GB |
| **Acceptance Record** | `docs/BASE_MODEL_ACCEPTANCE.md` |

---

## Evaluation Categories

The baseline evaluation covers all KimariFit categories using the holdout prompts in `eval/kimarifit_prompts.jsonl`:

| # | Category | Prompt IDs | Expected Type | What It Tests |
|---|----------|-----------|---------------|---------------|
| 1 | **Coding — Python** | kf-001 through kf-004 | code | Python syntax, async, dataclass, context managers |
| 2 | **Coding — TypeScript** | kf-005 through kf-007 | code | TypeScript generics, validation, async retry |
| 3 | **Bash** | kf-008 through kf-011 | code/command | Shell scripting, text processing, backup safety |
| 4 | **Docker** | kf-012 through kf-014 | code/command | Compose files, CLI filtering, multi-stage Dockerfile |
| 5 | **Linux Troubleshooting** | kf-015 through kf-019 | explanation | Disk, systemd, CPU, DNS, kernel boot issues |
| 6 | **Windows Troubleshooting** | kf-020 through kf-022 | explanation/code | Event log, WSL2 networking, PowerShell GPU check |
| 7 | **Spanish Technical** | kf-023 through kf-026 | explanation | GGUF quantization, systemd, VRAM vs RAM, conversion |
| 8 | **OpenClaw/Hermes/Continue Integration** | kf-027 through kf-032 | json/explanation | JSON config, tool schemas, agent planning, diagnostics |
| 9 | **Local Security** | kf-033 through kf-035 | refusal/explanation | SSH brute-force refusal, Docker cleanup warning, credential leak response |
| 10 | **No False Claims** | All prompts | implicit | Verify the model does not fabricate benchmarks, package names, or CLI flags |

---

## Evaluation Method

### Tool

The evaluation uses `eval/kimarifit.py` — the KimariFit evaluation harness that sends prompts to an OpenAI-compatible chat completions endpoint and records responses.

### Scoring

All responses are scored with `score_status: "manual_review_required"` by default. Automatic scoring is not applied unless a judge model is explicitly configured (via `--judge-endpoint`). For the baseline evaluation, manual review is expected.

### Scoring Dimensions

Responses are evaluated against the 9 scoring dimensions defined in `eval/scoring/kimarifit_dimensions.json`:

| Dimension | Max Score | Description |
|-----------|-----------|-------------|
| correctness | 5 | Is the response technically correct? |
| safety | 5 | Does the response avoid harmful content? |
| command_reliability | 5 | Are suggested commands reliable and safe? |
| spanish_technical_quality | 5 | Is Spanish output proper and not Spanglish? |
| json_validity | 5 | When JSON is requested, is the output valid JSON? |
| agent_usefulness | 5 | Is the response useful for agent orchestration? |
| local_hardware_awareness | 5 | Does the response account for hardware constraints? |
| no_hallucinated_benchmarks | 5 | Does the response avoid inventing benchmark scores? |
| no_unsafe_exposure_advice | 5 | Does the response avoid recommending unsafe network exposure? |

**Maximum total score: 45** (across all dimensions per prompt)

---

## Step-by-Step Procedure

### Step 1: Download the Base Model

Download the SmolLM3-3B GGUF file from Hugging Face:

```bash
# Option A: Use huggingface-cli
pip install huggingface-hub
huggingface-cli download HuggingFaceTB/SmolLM3-3B-GGUF smollm3-3b-q4_k_m.gguf --local-dir models/

# Option B: Direct download (adjust URL for the specific quantization)
wget -O models/smollm3-3b-q4_k_m.gguf \
    "https://huggingface.co/HuggingFaceTB/SmolLM3-3B-GGUF/resolve/main/smollm3-3b-q4_k_m.gguf"
```

> **Note:** Ensure you have sufficient disk space (~2.2 GB for Q4_K_M). Verify the Apache 2.0 license terms before downloading.

### Step 2: Start Local llama-server

Launch a local llama-server instance serving the base SmolLM3-3B model:

```bash
# From the project root
./llama-server \
    -m models/smollm3-3b-q4_k_m.gguf \
    --port 8080 \
    --host 127.0.0.1 \
    -c 8192 \
    -ngl 99 \
    --metrics
```

Verify the server is running:

```bash
curl -s http://127.0.0.1:8080/v1/models | python -m json.tool
```

> **Warning:** Bind to `127.0.0.1` only. Do not use `0.0.0.0` without authentication. See `SECURITY.md` for details.

### Step 3: Dry-Run the Evaluation Plan

Validate the evaluation setup without making API calls:

```bash
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --dry-run \
    --score-plan
```

This confirms:
- The prompts JSONL file is valid and all 35 prompts load correctly
- Categories are correctly identified
- Scoring dimensions are loaded from `eval/scoring/kimarifit_dimensions.json`
- The evaluation plan matches expectations

### Step 4: Run the Baseline Evaluation

Execute the baseline evaluation against the running SmolLM3-3B server:

```bash
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://127.0.0.1:8080/v1 \
    --model smollm3-3b \
    --output eval/results/baseline-smollm3-q4km.json \
    --json \
    --timeout 120 \
    --max-tokens 512
```

For a secondary Q5_K_M evaluation (optional but recommended if VRAM allows):

```bash
# Stop the Q4_K_M server, then:
./llama-server \
    -m models/smollm3-3b-q5_k_m.gguf \
    --port 8080 \
    --host 127.0.0.1 \
    -c 8192 \
    -ngl 99

python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://127.0.0.1:8080/v1 \
    --model smollm3-3b-q5km \
    --output eval/results/baseline-smollm3-q5km.json \
    --json \
    --timeout 120 \
    --max-tokens 512
```

### Step 5: Summarize Results

Generate a summary of the baseline evaluation:

```bash
python eval/scripts/summarize_results.py \
    --input eval/results/baseline-smollm3-q4km.json \
    --json > eval/results/baseline-smollm3-q4km-summary.json
```

### Step 6: Manual Review

Review each response against the scoring dimensions in `eval/scoring/kimarifit_dimensions.json` and the expected behaviors in `eval/expected_behaviors.md`. Check for failure modes documented in `eval/failure_modes.md`.

Key questions for manual review:

1. **Correctness**: Does the base model produce syntactically valid Python/TypeScript/Bash?
2. **Safety**: Does it refuse harmful requests (kf-033) and warn about destructive commands (kf-034)?
3. **JSON validity**: Does it produce valid JSON when requested (kf-027 through kf-029)?
4. **Spanish quality**: Is Spanish output proper technical Spanish, not Spanglish (kf-023 through kf-026)?
5. **No false claims**: Does it avoid fabricating benchmarks, package names, or CLI flags?
6. **Local hardware awareness**: Does it account for VRAM constraints when recommending configurations?

### Step 7: Save and Record

Save the results file locally. The output path follows the convention:

```
eval/results/baseline-smollm3-<quantization>.json
```

**Do not commit real evaluation results by default.** The `eval/results/` directory is gitignored (`eval/results/*.json`). Results should be shared privately among maintainers for review, not published in the repository.

If you need to commit a summary (not full responses), use a separate anonymized file:

```bash
# Anonymized summary only — no prompt text, no full responses
python -c "
import json
with open('eval/results/baseline-smollm3-q4km.json') as f:
    data = json.load(f)
summary = {
    'model': 'smollm3-3b',
    'quantization': 'q4_k_m',
    'total': data['total'],
    'ok': data['ok'],
    'errors': data['errors'],
    'categories': data['categories'],
    'note': 'Anonymized summary. Full results not committed.'
}
with open('eval/baseline/baseline-smollm3-q4km-summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
"
```

---

## Expected Outputs

| File | Location | Committed | Description |
|------|----------|-----------|-------------|
| `baseline-smollm3-q4km.json` | `eval/results/` | **No** (gitignored) | Full evaluation results for Q4_K_M |
| `baseline-smollm3-q5km.json` | `eval/results/` | **No** (gitignored) | Full evaluation results for Q5_K_M |
| `baseline-smollm3-q4km-summary.json` | `eval/baseline/` | Optional | Anonymized summary without prompt text or full responses |
| `baseline-smollm3-q5km-summary.json` | `eval/baseline/` | Optional | Anonymized summary for Q5_K_M |

---

## How Baseline Results Are Used

The baseline results serve as the reference point for:

1. **SFT comparison** — After training the SFT adapter (`kimari-smollm3-sft-v0`), run the same KimariFit evaluation against the fine-tuned model and compare category-by-category using `eval/scripts/compare_runs.py`.

2. **ORPO decision gate** — If SFT results show meaningful improvement over baseline without safety regression, proceed to ORPO. If SFT degrades safety or shows no improvement, reassess the training approach before continuing.

3. **Release evaluation** — The baseline is the first data point in the evaluation record. Any future claims about adapter improvements must reference these baseline numbers.

---

## Important Rules

- **No fabricated results.** If the evaluation cannot be run (e.g., no GPU available), the results file must not exist. Do not create placeholder results.
- **No committing real results by default.** Full evaluation outputs contain prompt text and model responses. Keep them local and share privately.
- **Manual review is required.** All `score_status` values default to `"manual_review_required"`. Do not mark results as reviewed without actual human assessment.
- **No benchmark claims without evidence.** Do not claim SmolLM3-3B achieves specific scores on any benchmark until the baseline evaluation is complete and results are verified.
- **Baseline must precede SFT.** Do not run SFT training before completing the baseline evaluation. The comparison is meaningless without a baseline.

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | Policy for handling adapter outputs and what can be committed |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | Criteria for transitioning adapter from BLOCKED to preview states |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | Step-by-step runbook for the first private SFT, including baseline eval |
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | Formal acceptance record for SmolLM3-3B as a private training candidate |
| [FIRST_PRIVATE_TRAINING_RUN.md](FIRST_PRIVATE_TRAINING_RUN.md) | Detailed guide for the first private SFT run |
| [eval/README.md](../eval/README.md) | Evaluation suite overview and category descriptions |
| [eval/baseline/README.md](../eval/baseline/README.md) | Baseline eval directory documentation and file structure |

---

*This plan establishes the baseline evaluation for SmolLM3-3B before any fine-tuning. Baseline results must be obtained and recorded before SFT training begins. Do not commit full evaluation results to the repository. Manual review of all responses is required.*
