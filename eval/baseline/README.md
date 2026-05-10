# Baseline Evaluation — SmolLM3-3B Before Fine-Tuning

> **Version:** v0.1.20-alpha  
> **Date:** 2026-05-22  
> **Status:** Baseline eval must be completed before SFT training begins

---

## Overview

This directory contains documentation and (optionally) anonymized summaries for the SmolLM3-3B baseline evaluation. The baseline measures the performance of the unmodified base model against the KimariFit evaluation suite, establishing a reference point for comparing fine-tuned adapters.

**No model has been fine-tuned yet.** The baseline evaluation measures raw SmolLM3-3B capability before any LoRA adapter is applied.

---

## Important: Outputs Are Not Committed

Full evaluation result files are stored in `eval/results/` which is gitignored (`eval/results/*.json`). This directory (`eval/baseline/`) may contain anonymized summaries that exclude prompt text and full model responses, but the full results are kept locally and shared privately among maintainers.

**Do not commit:**
- Full evaluation result JSON files (contain prompt text and model responses)
- Any file containing model responses to evaluation prompts
- Any file claiming benchmark scores that have not been manually verified

**You may commit:**
- This README file
- Anonymized summary files containing only category counts, OK/error rates, and manual review status
- No prompt text, no model responses, no unverified scores

---

## How to Compare with Adapter Results

After the SFT adapter (`kimari-smollm3-sft-v0`) is trained and evaluated, compare it against the baseline using the comparison script:

```bash
# Compare baseline vs SFT adapter results
python eval/scripts/compare_runs.py \
    --baseline eval/results/baseline-smollm3-q4km.json \
    --adapter eval/results/adapter-smollm3-sft-v0-q4km.json \
    --output eval/results/comparison-sft-v0-vs-baseline.json
```

The comparison script produces a category-by-category breakdown showing:

- OK count and error count per category for both baseline and adapter
- Delta (improvement or regression) per category
- Overall improvement assessment
- Safety-specific checks (local_security, no_hallucinated_benchmarks, no_unsafe_exposure_advice)

For manual comparison, use the summarize script on both result files:

```bash
# Summarize baseline
python eval/scripts/summarize_results.py \
    --input eval/results/baseline-smollm3-q4km.json

# Summarize adapter
python eval/scripts/summarize_results.py \
    --input eval/results/adapter-smollm3-sft-v0-q4km.json
```

---

## Expected File Structure

```
eval/baseline/
├── README.md                                        # This file
├── baseline-smollm3-q4km-summary.json               # Anonymized Q4_K_M summary (optional)
└── baseline-smollm3-q5km-summary.json               # Anonymized Q5_K_M summary (optional)

eval/results/                                        # Full results (gitignored, not committed)
├── .gitkeep
├── baseline-smollm3-q4km.json                       # Full Q4_K_M baseline results
├── baseline-smollm3-q5km.json                       # Full Q5_K_M baseline results
├── baseline-smollm3-q4km-summary.json               # Q4_K_M summary
├── baseline-smollm3-q5km-summary.json               # Q5_K_M summary
├── adapter-smollm3-sft-v0-q4km.json                 # SFT adapter results
├── adapter-smollm3-sft-v0-q4km-summary.json         # SFT adapter summary
├── adapter-smollm3-orpo-v0-q4km.json                # ORPO adapter results (future)
└── comparison-sft-v0-vs-baseline.json               # Baseline vs SFT comparison
```

---

## Baseline Evaluation Categories

The baseline evaluation uses all 35 prompts from `eval/kimarifit_prompts.jsonl` across 10 categories:

| Category | Prompts | What It Measures |
|----------|---------|-----------------|
| python | kf-001 to kf-004 | Code generation, async, dataclass, context managers |
| typescript | kf-005 to kf-007 | Generics, validation, async retry |
| bash | kf-008 to kf-011 | Shell scripting, text processing, backup safety |
| docker | kf-012 to kf-014 | Compose files, CLI filtering, multi-stage Dockerfile |
| linux_troubleshooting | kf-015 to kf-019 | Disk, systemd, CPU, DNS, kernel boot |
| windows_troubleshooting | kf-020 to kf-022 | Event log, WSL2 networking, PowerShell GPU check |
| spanish_technical | kf-023 to kf-026 | GGUF, systemd, VRAM vs RAM, safetensors conversion |
| json_mode | kf-027 to kf-029 | JSON config, tool schemas, agent tool selection |
| openclaw_agent | kf-030 to kf-032 | Tool sequencing, health-check diagnostics, debugging |
| local_security | kf-033 to kf-035 | SSH refusal, Docker cleanup warning, credential leak |

---

## How to Run the Baseline Evaluation

See `docs/BASELINE_EVAL_PLAN.md` for the complete step-by-step procedure. The short version:

```bash
# 1. Start llama-server with SmolLM3-3B Q4_K_M
./llama-server -m models/smollm3-3b-q4_k_m.gguf --port 8080 --host 127.0.0.1 -c 8192 -ngl 99

# 2. Run the evaluation
python eval/kimarifit.py \
    --prompts eval/kimarifit_prompts.jsonl \
    --endpoint http://127.0.0.1:8080/v1 \
    --model smollm3-3b \
    --output eval/results/baseline-smollm3-q4km.json \
    --json \
    --timeout 120 \
    --max-tokens 512

# 3. Summarize results
python eval/scripts/summarize_results.py \
    --input eval/results/baseline-smollm3-q4km.json \
    --json > eval/results/baseline-smollm3-q4km-summary.json
```

---

## Anonymized Summary Format

If you create an anonymized summary for this directory, it should follow this format:

```json
{
  "model": "smollm3-3b",
  "quantization": "q4_k_m",
  "total_prompts": 35,
  "ok": 0,
  "errors": 0,
  "categories": {
    "python": { "total": 4, "ok": 0, "error": 0 },
    "typescript": { "total": 3, "ok": 0, "error": 0 },
    "bash": { "total": 4, "ok": 0, "error": 0 },
    "docker": { "total": 3, "ok": 0, "error": 0 },
    "linux_troubleshooting": { "total": 5, "ok": 0, "error": 0 },
    "windows_troubleshooting": { "total": 3, "ok": 0, "error": 0 },
    "spanish_technical": { "total": 4, "ok": 0, "error": 0 },
    "json_mode": { "total": 3, "ok": 0, "error": 0 },
    "openclaw_agent": { "total": 3, "ok": 0, "error": 0 },
    "local_security": { "total": 3, "ok": 0, "error": 0 }
  },
  "manual_review_required": true,
  "note": "Anonymized summary. Full results not committed. Scores require manual review."
}
```

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [docs/BASELINE_EVAL_PLAN.md](../../docs/BASELINE_EVAL_PLAN.md) | Complete baseline evaluation procedure |
| [docs/ADAPTER_ARTIFACT_POLICY.md](../../docs/ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed |
| [docs/ADAPTER_PREVIEW_GATE.md](../../docs/ADAPTER_PREVIEW_GATE.md) | Release state machine for adapters |
| [docs/PRIVATE_TRAINING_RUNBOOK.md](../../docs/PRIVATE_TRAINING_RUNBOOK.md) | Step-by-step training runbook |
| [eval/README.md](../README.md) | Evaluation suite overview |
| [eval/kimarifit.py](../kimarifit.py) | KimariFit evaluation harness |
| [eval/kimarifit_prompts.jsonl](../kimarifit_prompts.jsonl) | Evaluation prompt dataset |
| [eval/scoring/kimarifit_dimensions.json](../scoring/kimarifit_dimensions.json) | Scoring dimensions and criteria |

---

*This directory documents the SmolLM3-3B baseline evaluation. Full results are not committed to the repository. The baseline must be completed before SFT training begins so that adapter results can be compared against a known reference point.*
