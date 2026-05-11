# Private Eval Results Policy

> **Document Type:** Policy governing what evaluation results can be committed to the repository
> **Version:** v0.1.21-alpha
> **Date:** 2026-05-22
> **Status:** Active — governs all eval result commits

---

## Purpose

This policy defines what evaluation results from private training runs may be committed to the Kimari Local AI repository. The goal is to enable transparency and reproducibility while protecting sensitive information, private prompts, and preventing false claims.

---

## What CAN Be Committed

The following types of eval information are **safe to commit**:

| Type | Examples | Conditions |
|------|----------|------------|
| **Anonymous summaries** | "7 prompts evaluated, 4 ok, 3 errors" | Must not contain identifying information about prompts |
| **Category counts** | `{"python": 2, "bash": 2, "docker": 1, "spanish_technical": 2}` | Category names only, no prompt content |
| **Manual review status** | `manual_review_required: true` | Status flag only |
| **Hashes** | `adapter_sha256: "abc123..."` | SHA-256 hashes of adapter files for integrity verification |
| **Score status** | `score_status: "manual_review_required"` | Status flag only — no invented scores |
| **Run metadata** | `run_id`, `model_label`, `kimari_version`, `prompt_count` | Metadata fields only |
| **Configuration references** | `training_config: "training/configs/kimari_sft_lora.v0.example.yaml"` | File paths within repo only |
| **Error counts** | `errors: 3, missing_outputs: 2` | Aggregate numbers only |

---

## What CANNOT Be Committed

The following types of eval information are **NOT permitted in commits**:

| Type | Why Not | Example |
|------|---------|---------|
| **Private prompts** | Eval prompts may contain proprietary or sensitive instructions | `"prompt": "Configure the production database at db.internal.corp..."` |
| **Local paths** | Paths may expose internal infrastructure or usernames | `"model_path": "/home/admin/models/SmolLM3-3B"` |
| **Tokens or credentials** | Never commit authentication tokens or API keys | `"token": "hf_abc123..."` |
| **Sensitive outputs** | Model responses may contain real data, paths, or credentials | `"response": "The SSH key is -----BEGIN RSA PRIVATE KEY-----..."` |
| **Benchmark claims without review** | Unverified scores can mislead users about model capability | `"mmlu_score": 0.72` (without manual review) |
| **Full model responses** | May contain private information, hallucinated credentials, or harmful content | `"response": "To access the server, use ssh admin@192.168.1.1..."` |
| **Prompt text** | Even paraphrased prompts may reveal sensitive testing methodology | `"prompt": "Write a script to enumerate users on..."` |

---

## Committable Eval Summary Format

When committing eval results, use the `eval/templates/eval_summary.template.json` format. This format is designed to contain **only safe, aggregate information**:

```json
{
  "run_id": "kimari-smollm3-sft-v0-private-001",
  "model_label": "kimari-smollm3-sft-v0",
  "kimari_version": "0.1.21-alpha",
  "prompt_count": 7,
  "category_counts": {
    "python": 2,
    "bash": 2,
    "docker": 1,
    "spanish_technical": 2
  },
  "score_status": "manual_review_required",
  "manual_review_required": true,
  "safety_regression_detected": false,
  "false_claims_detected": false,
  "reviewer": "",
  "notes": ""
}
```

### Key Properties

1. **No raw prompts** — the `prompt` field from individual results is stripped
2. **No raw responses** — the `response` field from individual results is stripped
3. **No invented scores** — `score_status` is always `"manual_review_required"` until a human reviewer assigns scores
4. **No local paths** — only `run_id` and `model_label` identify the run, no filesystem paths
5. **No tokens** — no authentication or API information

---

## How to Create a Safe Eval Summary

Use the `eval/scripts/create_eval_summary.py` tool:

```bash
python eval/scripts/create_eval_summary.py \
    --input eval/results/sft-smollm3-001-raw.json \
    --output eval/results/sft-smollm3-001-summary.json
```

This script:
- Reads the raw eval result file
- Strips `prompt` and `response` fields from all results
- Produces a safe summary with category counts and review status
- Marks `manual_review_required: true` if no scores exist
- Does NOT invent scores

---

## Benchmark Claims Policy

No benchmark scores (MMLU, HumanEval, SWE-bench, KimariFit scores, or any other metric) may be:

1. **Claimed as official** without manual review by at least one reviewer
2. **Committed as verified** without a completed manual review record
3. **Published publicly** without passing through the adapter preview gate (see `docs/ADAPTER_PREVIEW_GATE.md`)

All benchmark scores in the repository must be marked with `score_status: "manual_review_required"` until a qualified human reviewer has verified them.

---

## Review Process

When eval results are committed:

1. **Create safe summary** using `create_eval_summary.py`
2. **Commit only the summary** — never the raw results
3. **Raw results stay local** — stored on the training machine, not in git
4. **Manual review** — a reviewer examines the raw results locally and updates the summary if appropriate
5. **No auto-promotion** — even positive eval results do not automatically advance the preview gate

---

## Enforcement

This policy is enforced by:

1. **`create_eval_summary.py`** — strips sensitive fields automatically
2. **`check-release.py`** — checks for suspicious content in eval result files
3. **PR review** — human reviewers verify no sensitive data is committed
4. **`.gitignore`** — raw eval result files with private content are gitignored

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | Governs what adapter artifacts can be committed |
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine for adapter release |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist for SFT run |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Baseline evaluation plan |
| [MODEL_HASHING.md](MODEL_HASHING.md) | SHA-256 hash procedures for model files |

---

*This policy governs what evaluation results may be committed to the repository. No private prompts, no local paths, no tokens, no sensitive outputs, and no benchmark claims without review. When in doubt, leave it out.*
