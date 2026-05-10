# Base Model Acceptance Record — SmolLM3-3B for First Private SFT

> **Document Type:** Formal acceptance record  
> **Version:** v0.1.19-alpha  
> **Date:** 2026-05-21  
> **Status:** Accepted for first private training run (**NOT** for public release)

---

## Decision

**Accepted for first private training run (NOT for public release).**

SmolLM3-3B is approved as the base model for the first private supervised fine-tuning (SFT) run only. This acceptance does **not** constitute approval for any form of public distribution, benchmarking claims, or Hugging Face release.

---

## Accepted Candidate

| Field | Value |
|-------|-------|
| **Model ID** | `smollm3-3b` |
| **Hugging Face Repo** | `HuggingFaceTB/SmolLM3-3B` |
| **Parameters** | ~3B |
| **License** | Apache 2.0 |
| **Context Length** | 16,384 tokens |
| **Tokenizer Family** | SmolLM |
| **Expected VRAM (Q4_K_M)** | ~2.2 GB |
| **Expected VRAM (Q5_K_M)** | ~2.7 GB |
| **Risk Level** | Low |

---

## Reason for Acceptance

SmolLM3-3B was selected as the first private training candidate based on the following factors:

1. **Apache 2.0 License** — Fully permissive license with clear terms for derivative distribution. This is the safest legal path among all evaluated candidates (see ADR-001 in `docs/MODEL_DECISION_RECORD.md`).

2. **3B-Class Model** — Fits within the 3B–4B parameter target for Kimari-4B. Suitable for LoRA fine-tuning on consumer hardware.

3. **GTX 1060/1080 Compatible** — At Q4_K_M quantization, the model requires approximately 2.2 GB VRAM, well within the 6 GB (GTX 1060) and 8 GB (GTX 1080) budgets. This leaves headroom for context length and batch size.

4. **Open Weights** — Model weights are publicly available on Hugging Face under a permissive license, enabling download, inspection, and fine-tuning without gated access.

5. **Long Context (16K)** — The 16,384 token context window is adequate for the Kimari use case (coding, system administration, agent tasks) and allows for multi-turn conversations at practical lengths.

6. **Lower Redistribution Friction** — Compared to candidates with restrictive licenses (Qwen's `qwen-research`, Meta's `Llama-3.2-Community-License`), Apache 2.0 imposes no MAU thresholds, no acceptable use policy, and no ambiguity about derivative work rights.

---

## Scope of Acceptance

This acceptance is **limited to**:

- Private, local supervised fine-tuning (SFT) using LoRA on the developer's hardware
- Evaluation of the resulting adapter using the KimariFit evaluation suite
- Internal experimentation to validate the training pipeline end-to-end
- Storing adapter output locally (not committed to the repository, not uploaded anywhere)

This acceptance does **NOT** extend to any form of public distribution or release.

---

## Explicit Exclusions

The following actions are **NOT** authorized under this acceptance:

| Exclusion | Reason |
|-----------|--------|
| **No published weights** | No fine-tuned weights (adapter or merged) may be uploaded to Hugging Face, any other platform, or shared publicly |
| **No real benchmark yet** | No benchmark scores may be claimed or published for the fine-tuned model until a formal evaluation is completed and documented |
| **No public release approved yet** | This acceptance does not constitute approval for public release. A separate release decision is required |

Anyone encountering Kimari-4B references in this repository should understand that **no model has been released** and **no weights are available**.

---

## Pre-Release Checklist

Before any public release of Kimari-4B (or any fine-tuned derivative of SmolLM3-3B), the following checklist must be completed in full:

- [ ] **Eval passed** — Full evaluation suite (`eval/run_eval.py`, `eval/kimarifit_prompts.jsonl`) completed with acceptable scores. Results must be real, measured values — not targets, estimates, or placeholders.
- [ ] **License verified** — Apache 2.0 license for SmolLM3-3B confirmed to cover derivative distribution of fine-tuned weights in all planned formats (safetensors, GGUF). Documented in `MODEL_LICENSES.md`.
- [ ] **Model card updated** — `MODEL_CARD.md` and Hugging Face model card updated with real training details, evaluation results, known limitations, and proper disclaimers.
- [ ] **Hashes generated** — SHA-256 hashes computed for all distributable files (safetensors, GGUF, tokenizer). Hashes must be verified, not fabricated. See `docs/MODEL_HASHING.md`.
- [ ] **HF files ready** — All required files for the Hugging Face repository are prepared and validated. See `docs/HUGGINGFACE_RELEASE.md` for the complete file list and upload checklist.
- [ ] **Safety review done** — Safety evaluation completed with acceptable results. No harmful outputs in standard test cases. See `SECURITY.md` for safety policy.

> **If any checklist item is incomplete, the public release must not proceed.** There are no exceptions.

---

## Final Base for Public Release

The final base model selection for public release of Kimari-4B remains subject to:

1. **Eval results** — SmolLM3-3B must demonstrate adequate baseline and post-fine-tuning performance. If evaluation results are insufficient, a different base model may be selected (see Qwen2.5-3B-Instruct and Llama-3.2-3B-Instruct as alternatives in `docs/MODEL_DECISION_RECORD.md`).

2. **License review** — A formal, documented review of the Apache 2.0 license as it applies to fine-tuned derivative works must be completed and recorded. While Apache 2.0 is expected to be permissive, the review must be explicit.

3. **Safety review** — The fine-tuned model must undergo safety evaluation before any public distribution. This includes testing for harmful outputs, bias, and failure modes documented in `eval/failure_modes.md`.

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [MODEL_DECISION_RECORD.md](MODEL_DECISION_RECORD.md) | ADR-001 — full candidate comparison and scoring that led to this acceptance |
| [FIRST_PRIVATE_TRAINING_RUN.md](FIRST_PRIVATE_TRAINING_RUN.md) | Step-by-step guide for the private SFT run authorized by this acceptance |
| [HF_PLACEHOLDER_PLAN.md](HF_PLACEHOLDER_PLAN.md) | Plan for Hugging Face placeholder repository (docs-only, no weights) |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full release checklist and process for when public release is authorized |
| [MODEL_LICENSES.md](../MODEL_LICENSES.md) | License layers and base model license details |
| [MODEL_HASHING.md](MODEL_HASHING.md) | SHA-256 hash procedures for model files |
| [training/configs/base_candidates.yaml](../training/configs/base_candidates.yaml) | Machine-readable candidate data including license verification status |

---

*This document constitutes a formal acceptance record for SmolLM3-3B as a private training candidate only. It does not constitute a commitment to any public release. No weights are available. No benchmarks are claimed. The pre-release checklist must be completed in full before any public distribution.*
