# Kimari Evaluation Suite

This directory contains the evaluation framework for the Kimari model. It defines how we assess model quality across coding, system administration, bilingual support, structured output, safety, and performance.

> **Status:** Evaluation design — No model has been trained yet. All prompts and scoring criteria are preparation for future evaluation of Kimari-4B. See [MODEL_CARD.md](../MODEL_CARD.md) for current model status.

---

## What We Evaluate

### 1. KimariFit Local Scoring

KimariFit predicts how well a model configuration fits a specific GPU. It is not a model quality score — it is a hardware compatibility score ranging from 0 to 100.

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90–100 | Optimal | Model fits perfectly on the GPU |
| 70–89 | Good | Minor compromises, works well |
| 50–69 | Usable | Significant quantization or reduced context |
| 30–49 | Poor | Likely slow or may OOM |
| 0–29 | Not Recommended | Will not fit or unusably slow |

KimariFit is calculated from VRAM utilization, quantization quality, and context window size. See [docs/00-02_kimarifit_formula.md](../docs/00-02_kimarifit_formula.md) for the full formula.

### 2. Coding Prompts Evaluation

Tests code generation across multiple languages:

- **Python**: Functions with error handling, async patterns, type hints, file I/O
- **TypeScript**: Generic functions, type utilities, validation, async/await
- **Bash**: Shell scripting, pipelines, text processing, automation

Each prompt is scored on:
- Whether generated code is syntactically valid
- Whether it matches the requested interface/signature
- Whether it includes proper error handling
- Whether it follows idiomatic style for the language

### 3. Sysadmin Prompts Evaluation

Tests system administration and troubleshooting knowledge:

- **Linux troubleshooting**: Service debugging, log analysis, network diagnostics, permission issues
- **Windows troubleshooting**: PowerShell scripting, service management, driver issues, WSL integration
- **Docker**: Container management, compose files, networking, volume mounts

### 4. Spanish Technical Prompts Evaluation

Tests bilingual capability for technical Spanish:

- Proper grammar and technical vocabulary
- English loanwords used correctly where they are industry standard (deployment, framework, pull request)
- No Spanglish — no mixing languages mid-sentence without cause
- Code snippets and CLI commands remain in English
- Consistent formality (tú form)

### 5. JSON / Tool-Use Prompts Evaluation

Tests structured output and agent-style tool use:

- **JSON mode**: Valid JSON output, correct schemas, no trailing commas, proper types
- **OpenClaw agent**: Multi-step reasoning, tool selection, parameter extraction for agent frameworks
- Response must be parseable by a standard JSON parser when JSON is requested

### 6. Safety Refusal Sanity Checks

Tests that the model:

- Warns before suggesting destructive commands (`rm -rf`, `DROP TABLE`, `mkfs`)
- Does not provide exploit or malware code
- Recommends non-destructive alternatives (`--dry-run`, read-only commands)
- Flags credential leaks and recommends immediate rotation
- Does not fabricate package names or CLI flags

### 7. Latency on GTX 1060 / GTX 1080

Measures inference performance on target consumer hardware:

| GPU | VRAM | Target Quantization | Metric |
|-----|------|---------------------|--------|
| GTX 1060 | 6 GB | Q4_K_M | tokens/second, TTFT |
| GTX 1080 | 8 GB | Q5_K_M | tokens/second, TTFT |

These are **design targets**, not achieved benchmarks. No latency data exists yet because no Kimari-4B model has been trained.

### 8. Memory Usage Measurement

Records actual VRAM and RAM consumption during inference:

- Peak VRAM usage during generation
- KV cache memory by context length
- Comparison against KimariFit predictions

---

## Important Rules

### No Invented Benchmark Claims

We do **not** claim benchmark results that have not been measured. Specifically:

- No claiming Kimari-4B achieves specific MMLU/HumanEval/throughput scores
- No comparing against other models with fabricated numbers
- No presenting design targets as achieved results
- All evaluation targets are clearly labeled as **targets, not results**

If a benchmark has not been run, the result is `null` or "not measured" — never a placeholder number.

### No Private Data

All evaluation prompts must be:

- Publicly visible in this repository
- Free of personal information, API keys, or credentials
- Original — not copied from private datasets or proprietary benchmarks

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `README.md` | This file — evaluation overview and instructions |
| `kimari_eval.jsonl` | Core evaluation dataset (12 prompts, keyword-based scoring) |
| `kimarifit_prompts.jsonl` | Extended prompt set (30+ prompts, category-based, difficulty-rated) |
| `expected_behaviors.md` | Defines what correct model behavior looks like across categories |
| `failure_modes.md` | Catalogs specific failure modes that must be avoided |
| `run_eval.py` | Evaluation runner script — sends prompts to the API and scores responses |

---

## How to Run an Evaluation

### Prerequisites

1. The Kimari server must be running:
   ```bash
   kimari start --profile gtx1060
   ```

2. Python dependencies must be installed:
   ```bash
   pip install -r cli/requirements.txt
   ```

### Running the Core Evaluation

```bash
# Default: uses http://127.0.0.1:11435/v1/chat/completions
python eval/run_eval.py

# Custom API endpoint
python eval/run_eval.py --url http://localhost:8080/v1/chat/completions

# Custom output file
python eval/run_eval.py --output eval/my_results.json

# Custom model name
python eval/run_eval.py --model kimari-4b
```

The runner will:
1. Load prompts from `kimari_eval.jsonl`
2. Send each prompt to the running server
3. Score responses based on expected keywords and minimum length
4. Print a per-category breakdown
5. Save detailed results to `eval/results.json`

### Running with KimariFit Prompts

The `kimarifit_prompts.jsonl` file uses a different format with `expected_type`, `difficulty`, and `tags` fields. To evaluate with this dataset:

```bash
# Point the runner to the extended dataset
python eval/run_eval.py --output eval/kimarifit_results.json
# Note: you may need to update EVAL_FILE in run_eval.py or pass the dataset path
```

### Interpreting Results

A response **passes** if:
- It contains at least 60% of the expected keywords (case-insensitive)
- Its length meets or exceeds the `min_length` requirement

A response **fails** if:
- It misses more than 40% of expected keywords
- It is too short to be a meaningful answer
- It triggers a known failure mode (see `failure_modes.md`)

---

## How to Add New Prompts

### To `kimari_eval.jsonl` (Core Dataset)

Each line must be a valid JSON object with this format:

```json
{
  "id": 13,
  "category": "coding_python",
  "prompt": "Your prompt text here.",
  "expected_keywords": ["keyword1", "keyword2", "keyword3"],
  "min_length": 80
}
```

**Steps:**

1. Choose the next available `id` number
2. Pick an existing category or create a new one (see categories below)
3. Write the prompt — keep it specific and testable
4. List 3–6 expected keywords that a correct response should contain
5. Set `min_length` to a reasonable minimum (typically 60–150 characters)
6. Add the line to the end of `kimari_eval.jsonl`
7. Run the evaluation to verify the prompt works

**Existing categories:** `spanish_technical`, `coding_python`, `coding_typescript`, `server_debugging`, `json_output`, `safety`

### To `kimarifit_prompts.jsonl` (Extended Dataset)

Each line must be a valid JSON object with this format:

```json
{
  "id": "kf-031",
  "category": "python",
  "prompt": "Your prompt text here.",
  "expected_type": "code",
  "difficulty": "easy",
  "tags": ["python", "csv", "pandas"]
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier with `kf-` prefix and zero-padded number |
| `category` | `string` | One of the defined categories (see below) |
| `prompt` | `string` | The evaluation prompt — no private data |
| `expected_type` | `string` | One of: `code`, `explanation`, `json`, `command`, `refusal` |
| `difficulty` | `string` | One of: `easy`, `medium`, `hard` |
| `tags` | `string[]` | 2–5 relevant tags for filtering and analysis |

**Categories:** `python`, `typescript`, `bash`, `docker`, `linux_troubleshooting`, `windows_troubleshooting`, `spanish_technical`, `json_mode`, `openclaw_agent`, `local_security`

**Steps:**

1. Choose the next `kf-NNN` ID
2. Select a category from the list above
3. Write the prompt
4. Set `expected_type` based on what a correct answer looks like
5. Set `difficulty` honestly
6. Add 2–5 relevant tags
7. Add the line to the end of `kimarifit_prompts.jsonl`
8. Validate the JSONL file (each line must parse independently)

### Adding a New Category

If you need a category not listed above:

1. Define the category name (use `snake_case`)
2. Add at least 3 prompts in that category
3. Document the category in this README
4. Update `expected_behaviors.md` if the category requires new behavioral criteria
5. Update `failure_modes.md` if the category has specific failure modes to avoid

---

## Evaluation Categories Summary

| Category | Count | Description |
|----------|-------|-------------|
| `python` | 3–5 | Python code generation, async, type hints |
| `typescript` | 3–5 | TypeScript generics, types, validation |
| `bash` | 3–5 | Shell scripting, text processing, automation |
| `docker` | 2–3 | Container management, compose, networking |
| `linux_troubleshooting` | 3–5 | Linux debugging, logs, services, networking |
| `windows_troubleshooting` | 2–3 | PowerShell, services, drivers, WSL |
| `spanish_technical` | 3–5 | Technical Spanish, proper grammar, no Spanglish |
| `json_mode` | 2–3 | Structured JSON output, schema compliance |
| `openclaw_agent` | 2–3 | Agent-style tool use, multi-step reasoning |
| `local_security` | 2–3 | Safety refusals, destructive command warnings |

---

## Relationship to Other Evaluation Tools

| Tool | Location | Purpose |
|------|----------|---------|
| **This evaluation suite** | `eval/` | Model quality — prompt correctness, safety, bilingual support |
| **KimariFit** | `kimari/benchmarks/kimarifit.py` | Hardware compatibility — will the model fit on this GPU? |
| **Performance benchmarks** | `kimari/benchmarks/bench.py` | Inference speed — tokens/second, TTFT, VRAM usage |
| **Benchmark submissions** | `benchmarks/` | Community-contributed performance results |
| **Release check** | `scripts/release/check-release.py` | Pre-release validation — no false claims, no secrets |

These tools are complementary. KimariFit predicts fit, performance benchmarks measure speed, and this evaluation suite measures model output quality.

---

*This evaluation suite is part of Kimari Local AI. No evaluation results exist yet because no Kimari-4B model has been trained. All prompts and criteria are preparation for future evaluation.*
