# Adapter Preview Gate — Release State Machine

> **Document Type:** Release gate criteria  
> **Version:** v0.1.20-alpha  
> **Date:** 2026-05-22  
> **Status:** Active — all adapters start in BLOCKED state

---

## Overview

The Adapter Preview Gate is a state machine that governs the visibility and distribution of trained adapter artifacts. Every adapter begins in the `BLOCKED` state and can only progress through explicit human decisions. There are **no automatic transitions**.

This gate exists to ensure that:

1. No adapter is shared publicly before it has been evaluated
2. No safety regression goes undetected
3. No license or legal issues are discovered after distribution
4. No false claims about model capability are made
5. Every transition is traceable to a human decision

---

## States

| State | Description |
|-------|-------------|
| **BLOCKED** | Default state. No sharing, no upload, no public visibility. The adapter exists locally only. |
| **PENDING** | Preliminary checks passed. The adapter is eligible for evaluation but still not shared. |
| **APPROVED_FOR_PRIVATE_TESTING** | Evaluation complete and acceptable. The adapter may be shared with designated private testers under NDA or equivalent trust. |
| **APPROVED_FOR_PUBLIC_PREVIEW** | All reviews passed. The adapter may be published as a public preview (e.g., on Hugging Face with appropriate disclaimers). |

---

## State Diagram

```
                    ┌─────────┐
                    │ BLOCKED │  ← Default state for all new adapters
                    └────┬────┘
                         │
           ┌─────────────▼─────────────┐
           │  Requirements:             │
           │  • License verified        │
           │  • No secrets/data issues  │
           │  • Adapter size recorded   │
           │  • Adapter hash recorded   │
           └─────────────┬─────────────┘
                         │
                    ┌────▼─────┐
                    │ PENDING  │
                    └────┬─────┘
                         │
           ┌─────────────▼─────────────┐
           │  Requirements:             │
           │  • Baseline comparison     │
           │  • KimariFit manual review │
           │  • No safety regression    │
           │  • No false claims         │
           └─────────────┬─────────────┘
                         │
           ┌─────────────▼──────────────────────┐
           │  APPROVED_FOR_PRIVATE_TESTING       │
           └────┬────────────────────────────────┘
                │
           ┌────▼──────────────────────────────┐
           │  Requirements:                     │
           │  • Model card updated              │
           │  • HF placeholder reviewed         │
           │  • Maintainer approval             │
           │  • Safety review passed            │
           └────┬──────────────────────────────┘
                │
           ┌────▼──────────────────────────────┐
           │  APPROVED_FOR_PUBLIC_PREVIEW       │
           └───────────────────────────────────┘
```

---

## Transition Requirements

### BLOCKED → PENDING

An adapter may transition from BLOCKED to PENDING when **all** of the following are satisfied:

| # | Requirement | How to Verify | Responsible |
|---|-------------|---------------|-------------|
| 1 | **License verified** | The base model license (Apache 2.0 for SmolLM3-3B) has been reviewed and confirmed to permit the current use (private evaluation of derivative weights). Documented in `MODEL_LICENSES.md`. | Maintainer |
| 2 | **No secrets or data issues** | A scan of the adapter directory reveals no API keys, tokens, user data, or proprietary content. Run `scripts/release/check-release.py` to verify. | Maintainer |
| 3 | **Adapter size recorded** | The total size of the adapter directory and the size of `adapter_model.safetensors` are recorded in the adapter manifest. | Maintainer |
| 4 | **Adapter hash recorded** | SHA-256 hashes of `adapter_model.safetensors` and `adapter_config.json` are computed and recorded in the adapter manifest. See `docs/MODEL_HASHING.md`. | Maintainer |

**Decision**: A human maintainer must explicitly approve the transition. The decision and date are recorded in the adapter manifest.

### PENDING → APPROVED_FOR_PRIVATE_TESTING

An adapter may transition from PENDING to APPROVED_FOR_PRIVATE_TESTING when **all** of the following are satisfied:

| # | Requirement | How to Verify | Responsible |
|---|-------------|---------------|-------------|
| 1 | **Baseline comparison done** | The adapter has been evaluated using KimariFit (`eval/kimarifit.py`) and the results have been compared against the baseline evaluation (`eval/results/baseline-smollm3-*.json`). The comparison shows measurable improvement in at least one category with no unexplained regressions. | Maintainer + Reviewer |
| 2 | **KimariFit manual review done** | All 35 prompts from `eval/kimarifit_prompts.jsonl` have been manually reviewed against the scoring dimensions in `eval/scoring/kimarifit_dimensions.json`. Each response has been assessed for correctness, safety, and quality. | Reviewer |
| 3 | **No regression in safety** | The safety-related categories (`local_security`, `no_hallucinated_benchmarks`, `no_unsafe_exposure_advice`) show no regression compared to baseline. The adapter must refuse harmful requests (kf-033) and warn about destructive commands (kf-034) at least as well as the base model. The `safety_regression_detected` field in eval results must be `false`. | Reviewer |
| 4 | **No false claims** | The adapter does not fabricate benchmark scores, package names, CLI flags, or error messages. Verified through manual review of all responses against `eval/failure_modes.md`. | Reviewer |

**Decision**: A human maintainer and at least one reviewer must explicitly approve the transition. Both decisions and dates are recorded.

### APPROVED_FOR_PRIVATE_TESTING → APPROVED_FOR_PUBLIC_PREVIEW

An adapter may transition from APPROVED_FOR_PRIVATE_TESTING to APPROVED_FOR_PUBLIC_PREVIEW when **all** of the following are satisfied:

| # | Requirement | How to Verify | Responsible |
|---|-------------|---------------|-------------|
| 1 | **Model card updated** | `MODEL_CARD.md` has been updated with real evaluation results, training details, known limitations, and proper disclaimers. No placeholder or TBD content. | Maintainer |
| 2 | **HF placeholder reviewed** | The Hugging Face placeholder repository plan (`docs/HF_PLACEHOLDER_PLAN.md`) has been reviewed and the repository is ready for the preview (if applicable). No weights are uploaded until the full release process in `docs/HUGGINGFACE_RELEASE.md` is followed. | Maintainer |
| 3 | **Maintainer approval** | The project maintainer has explicitly approved the public preview in writing (e.g., PR comment, signed document, or recorded meeting notes). | Maintainer |
| 4 | **Safety review passed** | A dedicated safety review has been completed, confirming that the adapter does not produce harmful outputs in standard test cases. This includes testing against the safety prompts in `eval/kimarifit_prompts.jsonl` and any additional edge cases identified during private testing. | Safety Reviewer |

**Decision**: The project maintainer must provide explicit written approval. The decision, date, and rationale are recorded in the adapter manifest.

---

## No Automatic Transitions

**All state transitions require explicit human decisions.** There is no script, CI job, or automated process that can advance an adapter from one state to another.

Specifically:

- Completing a training run does NOT automatically move the adapter out of BLOCKED
- Creating a manifest with `create_adapter_manifest.py` does NOT advance the gate — it records metadata but the adapter remains BLOCKED
- Passing automated tests does NOT automatically move the adapter to PENDING
- Positive evaluation results do NOT automatically move the adapter to APPROVED_FOR_PRIVATE_TESTING
- Private tester feedback does NOT automatically move the adapter to APPROVED_FOR_PUBLIC_PREVIEW

Every transition requires:

1. A human to verify the requirements are met
2. A human to make the decision
3. The decision to be recorded in the adapter manifest with the date and the name of the decision-maker

---

## Reverting States

An adapter may be reverted to a previous state if new information justifies it:

| Reversion | Trigger |
|-----------|---------|
| PENDING → BLOCKED | License concern identified, secret/data leak discovered, hash mismatch |
| APPROVED_FOR_PRIVATE_TESTING → PENDING | Safety regression discovered, evaluation error found, false claim detected |
| APPROVED_FOR_PUBLIC_PREVIEW → APPROVED_FOR_PRIVATE_TESTING | Safety issue reported by testers, model card inaccuracy discovered |
| Any state → BLOCKED | Critical safety failure, legal issue, or data contamination discovered |

Reversions follow the same requirements as transitions: explicit human decision, recorded in the adapter manifest with date and rationale.

---

## Recording State Changes

All state changes are recorded in the adapter manifest file:

```yaml
# training/adapters/kimari-smollm3-sft-v0/MANIFEST.yaml
adapter_name: kimari-smollm3-sft-v0
preview_gate_state: BLOCKED  # Current state
state_history:
  - state: BLOCKED
    date: "2026-05-22"
    actor: maintainer
    reason: "Initial state after training"
  # Future transitions are appended here:
  # - state: PENDING
  #   date: "2026-05-23"
  #   actor: maintainer
  #   reason: "License verified, no secrets, hashes recorded"
```

---

## What Each State Permits

| Action | BLOCKED | PENDING | APPROVED_FOR_PRIVATE_TESTING | APPROVED_FOR_PUBLIC_PREVIEW |
|--------|---------|---------|------------------------------|----------------------------|
| Store adapter locally | ✅ | ✅ | ✅ | ✅ |
| Run local evaluation | ✅ | ✅ | ✅ | ✅ |
| Record hashes | ✅ | ✅ | ✅ | ✅ |
| Commit manifest (no weights) | ✅ | ✅ | ✅ | ✅ |
| Commit anonymized eval summary | ❌ | ✅ | ✅ | ✅ |
| Share adapter privately (NDA/trust) | ❌ | ❌ | ✅ | ✅ |
| Upload to Hugging Face | ❌ | ❌ | ❌ | ✅ (with disclaimers) |
| Claim benchmark scores publicly | ❌ | ❌ | ❌ | ✅ (verified only) |
| Distribute GGUF quantizations | ❌ | ❌ | ❌ | ✅ (via HF only) |

---

## Relationship to Other Documents

| Document | Relationship |
|----------|-------------|
| [ADAPTER_ARTIFACT_POLICY.md](ADAPTER_ARTIFACT_POLICY.md) | Defines what can and cannot be committed, naming conventions, and hash recording |
| [BASELINE_EVAL_PLAN.md](BASELINE_EVAL_PLAN.md) | The baseline evaluation must be completed before PENDING → APPROVED_FOR_PRIVATE_TESTING |
| [PRIVATE_TRAINING_RUNBOOK.md](PRIVATE_TRAINING_RUNBOOK.md) | References this gate at every decision point in the training runbook |
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | The base model must be formally accepted before any adapter enters PENDING |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full release process for when an adapter reaches APPROVED_FOR_PUBLIC_PREVIEW |
| [HF_PLACEHOLDER_PLAN.md](HF_PLACEHOLDER_PLAN.md) | Placeholder repository rules for before any weights are distributed |
| [MODEL_LICENSES.md](../MODEL_LICENSES.md) | License verification is a prerequisite for BLOCKED → PENDING |

---

## Template References

The following templates are used in the gate process:

| Template | Path | Usage |
|----------|------|-------|
| Adapter manifest | `training/templates/adapter_manifest.template.yaml` | Used by `create_adapter_manifest.py` to generate adapter manifests with correct BLOCKED state |
| Eval summary | `eval/templates/eval_summary.template.json` | Used by `create_eval_summary.py` to produce committable eval summaries without sensitive data |

Creating a manifest or eval summary does NOT advance the gate. These are documentation tools only — all state transitions require explicit human decisions.

---

*This gate governs all adapter release decisions. No automatic transitions are permitted. Every state change requires explicit human approval, recorded with date, actor, and rationale. All adapters start in the BLOCKED state by default.*
