# SFT to ORPO Decision Framework

> **Document Type:** Decision framework for proceeding to preference tuning after SFT
> **Version:** v0.1.21-alpha
> **Date:** 2026-05-22
> **Status:** Active — governs whether ORPO/DPO proceeds after SFT

---

## Purpose

This document defines the decision framework for whether preference tuning (ORPO or DPO) should proceed after the first SFT run completes. It establishes clear go/no-go criteria based on SFT results, dataset quality, and safety considerations.

**ORPO/DPO is not guaranteed to run after SFT.** The SFT results must meet specific criteria before preference tuning is considered.

---

## Decision Table

| # | SFT Outcome | Decision | Rationale |
|---|-------------|----------|-----------|
| 1 | SFT improves instruction following but worsens safety | **No ORPO yet** | Safety regression must be addressed before adding complexity. Review and fix safety in SFT data/config first. |
| 2 | SFT improves coding/sysadmin capability and does NOT worsen safety | **Consider ORPO** | Positive signal. Proceed to evaluate preference data quality before committing to ORPO. |
| 3 | SFT overfits on dataset v0 | **Expand dataset before ORPO** | Overfitting means the model memorized training data rather than learning generalizable skills. Adding preference tuning on top of an overfit model wastes compute and risks worse outcomes. |
| 4 | Baseline surpasses adapter on key metrics | **Review dataset/config** | If the base model outperforms the fine-tuned adapter, something is wrong. Do not proceed to ORPO — investigate and fix the SFT pipeline first. |
| 5 | SFT shows no measurable improvement over baseline | **Review dataset/config** | Neutral or negative SFT results indicate problems with data quality, hyperparameters, or methodology. ORPO cannot fix a broken SFT foundation. |
| 6 | SFT results are mixed (some categories improve, others regress) | **Selective review** | Evaluate per-category. If regressions are limited to non-critical categories and improvements are substantial, consider ORPO with caution. Document all regressions. |

---

## Prerequisites for ORPO

Even if SFT results are positive, ORPO should only proceed if **all** of the following are met:

| # | Prerequisite | How to Verify |
|---|-------------|---------------|
| 1 | `preference_v0` dataset has sufficient quality | Run `training/scripts/validate_training_ready.py --preference dataset/v0/preference_v0.jsonl` — minimum 20 records, all with source/license fields, no forbidden strings |
| 2 | `preference_v0` has meaningful chosen/rejected pairs | Manual review of at least 10 pairs — the chosen response should be genuinely better, not arbitrary |
| 3 | SFT adapter is stable (no safety regression) | KimariFit eval shows no regression in safety categories compared to baseline |
| 4 | SFT adapter manifest has been created | `MANIFEST.yaml` exists with hashes, sizes, and BLOCKED state |
| 5 | Baseline eval is complete | `eval/results/baseline-smollm3-*.json` exists with valid results |
| 6 | SFT eval is complete | `eval/results/sft-smollm3-*.json` exists with valid results |
| 7 | Compute budget available | ORPO requires comparable GPU time to SFT |

---

## ORPO vs DPO Selection

If preference tuning proceeds, the choice between ORPO and DPO depends on:

| Factor | DPO | ORPO |
|--------|-----|------|
| Memory usage | Higher (requires reference model) | Lower (no reference model needed) |
| Training stability | More established | Newer, less proven |
| Data requirements | Same preference pairs | Same preference pairs |
| Recommended GPU | 40 GB+ | 24 GB+ |
| Implementation maturity | Well-tested in trl | Available in trl, less battle-tested |

**Recommendation for first run:** Use DPO if 40 GB+ GPU is available. Use ORPO if only 24 GB GPU. Neither method is selected yet — this is a planning reference only.

---

## ORPO Does Not Run in CI

Preference tuning (ORPO, DPO, or any RL method) will **never** run in CI:

- No GPU available in CI
- No model downloads in CI
- Training is a manual, human-supervised process
- Results require manual review before any action is taken

---

## Decision Flowchart

```
                    ┌─────────────────┐
                    │  SFT Complete    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Safety OK?       │
                    │ (No regression)  │
                    └──┬──────────┬───┘
                  Yes  │          │  No
                       │          │
              ┌────────▼──┐   ┌──▼─────────────┐
              │ SFT >     │   │ No ORPO yet    │
              │ Baseline? │   │ Fix safety     │
              └──┬─────┬──┘   └────────────────┘
              Yes │     │ No
                  │     │
         ┌────────▼──┐  ┌▼───────────────────┐
         │ Overfit?  │  │ Review dataset/    │
         │           │  │ config before ORPO │
         └──┬────┬───┘  └────────────────────┘
         Yes │    │ No
             │    │
    ┌────────▼──┐ ┌▼──────────────────┐
    │ Expand    │ │ preference_v0     │
    │ dataset   │ │ sufficient?       │
    │ first     │ └──┬────────────┬───┘
    └───────────┘ Yes │            │ No
                     │            │
           ┌─────────▼──┐  ┌─────▼─────────┐
           │ Consider    │  │ Build more    │
           │ ORPO/DPO    │  │ preference    │
           └─────────────┘  │ data first    │
                            └───────────────┘
```

---

## What ORPO Cannot Fix

Preference tuning (ORPO or DPO) is not a solution for:

- **Poor SFT data quality** — garbage in, garbage out
- **Safety regressions** — ORPO does not inherently improve safety; it shapes preference
- **Overfitting** — adding ORPO on top of an overfit model compounds the problem
- **Missing capabilities** — if SFT didn't teach a skill, ORPO won't add it
- **Dataset bias** — ORPO amplifies the preferences in the data; biased data → biased output

---

## Checklist Before Starting ORPO

- [ ] SFT results reviewed and documented
- [ ] No safety regression in SFT adapter vs baseline
- [ ] SFT adapter shows measurable improvement in at least one target category
- [ ] `preference_v0` dataset validated (minimum 20 records, quality reviewed)
- [ ] Compute budget confirmed for ORPO run
- [ ] ORPO config (`training/configs/kimari_orpo.v0.example.yaml`) reviewed
- [ ] Run config created for ORPO with `public_release_allowed: false` and `hf_upload_allowed: false`
- [ ] Preview gate for SFT adapter is at least BLOCKED (no need to advance to PENDING before ORPO)
- [ ] Baseline and SFT eval results available for comparison

---

## v0.1.22-alpha Additions

The following safeguards were introduced in v0.1.22-alpha to prevent premature or unsafe ORPO transitions:

- **ORPO decision is deferred until postrun summary is reviewed.** The post-training orchestration script (`training/scripts/postrun_private_sft.py`) produces a structured summary that must be reviewed by a human before any ORPO proceed decision is made. There is no automatic transition from SFT completion to ORPO launch.

- **If `manual_review_required=true` in the eval summary, no automatic ORPO proceed.** When the evaluation summary indicates that manual review has not been completed, the ORPO decision is held regardless of how favorable the numeric scores appear. A human must explicitly review and clear the flag before ORPO can be considered.

- **If `safety_regression_detected=true` in the eval summary, ORPO is blocked.** Any detected safety regression is a hard block on proceeding to ORPO. The SFT data, config, and training pipeline must be investigated and the regression resolved before the ORPO decision can be revisited.

- **`postrun_private_sft.py` can orchestrate post-training evaluation.** This script automates the sequence of post-SFT steps (eval execution, summary generation, manifest creation, ORPO decision check) and enforces the gates described above. It does **not** bypass any decision — it surfaces the data needed for a human decision.

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_PREVIEW_GATE.md](ADAPTER_PREVIEW_GATE.md) | State machine governing adapter release |
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | What can and cannot be committed |
| [PRIVATE_SFT_EXECUTION_CHECKLIST.md](PRIVATE_SFT_EXECUTION_CHECKLIST.md) | Pre-flight checklist for SFT run |
| [MODEL_TRAINING_PLAN.md](MODEL_TRAINING_PLAN.md) | Full training plan including ORPO phase |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | Baseline evaluation plan |
| [PRIVATE_EVAL_RESULTS_POLICY.md](PRIVATE_EVAL_RESULTS_POLICY.md) | What eval results can be committed |

---

*This framework governs the decision to proceed from SFT to preference tuning. ORPO/DPO is not automatic after SFT. All criteria must be met and the decision must be documented. DPO/ORPO does not run in CI.*
