# Hugging Face Placeholder Plan — smouj/kimari-4b

> **Document Type:** Placeholder repository plan  
> **Version:** v0.1.19-alpha  
> **Date:** 2026-05-21  
> **Status:** Planning — no repository has been created

---

## Overview

This document defines what is allowed and what is NOT allowed in the planned Hugging Face repository `smouj/kimari-4b` during the placeholder phase — before any model weights are ready for release.

The placeholder repository signals **intent** to release a model in the future, without distributing any weights, adapters, quantized files, or fabricated benchmarks.

---

## Planned Repository

| Field | Value |
|-------|-------|
| **Repository** | `smouj/kimari-4b` |
| **Platform** | Hugging Face Hub |
| **Status** | Not created yet |
| **Purpose** | Docs-only placeholder signaling future model release |

---

## When to Create

The placeholder repository may be created **after** both of the following conditions are met:

1. **Base model accepted** — SmolLM3-3B formally accepted for private training (see `docs/BASE_MODEL_ACCEPTANCE.md`)
2. **License reviewed** — Apache 2.0 license reviewed and confirmed to cover derivative distribution of fine-tuned weights

Do not create the repository before these conditions are satisfied.

---

## Allowed Files (Placeholder Phase)

During the placeholder phase, the repository may contain **only** the following documentation files:

| File | Description |
|------|-------------|
| `README.md` | Placeholder model card. Must clearly state that no weights are available, no model has been trained yet, and the repository is docs-only. Must not claim capabilities or benchmarks that do not exist. |
| `MODEL_CARD.md` | Extended model card pointing to the Kimari project repository (`https://github.com/smouj/kimari-local-ai`) for the latest status. Must include "NOT YET AVAILABLE" disclaimers. |
| `MODEL_LICENSES.md` | License layer documentation. References the base model license (Apache 2.0 for SmolLM3-3B) and the Kimari software license (MIT). Must be accurate — no placeholder or TBD license claims. |
| `docs/HUGGINGFACE_RELEASE.md` | Summary of the full release process as documented in the Kimari repository. Serves as a reference for when the actual release happens. |

**All placeholder files must:**

- Clearly state that no model weights are available
- Not claim any benchmarks, capabilities, or performance metrics that do not exist
- Include the date of last update
- Link to the Kimari project repository for current status
- Not mislead users into believing a model is available for download

---

## NOT Allowed (Placeholder Phase)

The following files must **NOT** be present in the repository during the placeholder phase:

| Prohibited | Reason |
|------------|--------|
| **Weights** (safetensors, bin, pt) | No model has been trained or evaluated yet |
| **Adapters** (LoRA, QLoRA) | Private training output is not for distribution |
| **GGUF files** | No quantized model exists |
| **Fake benchmarks** | Fabricating benchmark results is dishonest and potentially misleading |
| **Config files requiring weights** | Implies a model is available |
| **Tokenizer files without weights** | Suggests a working model when none exists |
| **Training data** | License and privacy restrictions |
| **HF API tokens** | Security vulnerability — never commit secrets |

> **If any prohibited file is found in the placeholder repository, it must be removed immediately.**

---

## No Token Committed

- Hugging Face API tokens must **never** be committed to any repository (neither the Kimari Git repository nor the HF repository).
- Tokens must be stored in environment variables or a credential manager.
- CI/CD pipelines must use repository secrets, not hardcoded tokens.
- The `check-release.py` script includes checks for leaked secrets.

---

## No Automated Upload

- There is **no automated upload pipeline** from the Kimari repository to Hugging Face.
- All uploads to the HF repository must be **manual and intentional**.
- No CI job, GitHub Action, or script should push files to Hugging Face automatically.
- Any upload must be preceded by a manual review of the pre-release checklist in `docs/BASE_MODEL_ACCEPTANCE.md`.

---

## Placeholder Is Docs-Only

The placeholder repository serves one purpose: **signaling intent without distributing anything.**

It communicates to the community:

1. A model named Kimari-4B is planned
2. The project is actively working on training
3. No weights, adapters, or quantized files are available yet
4. The release process will follow the documented checklist
5. Interested users can follow progress at the Kimari project repository

It does **NOT** communicate:

- That a model is available for download
- That any benchmarks or capabilities have been measured
- That a release date has been set
- That any training has completed successfully

---

## Transition to Full Release

When the pre-release checklist in `docs/BASE_MODEL_ACCEPTANCE.md` is fully satisfied, the placeholder repository will transition to a full release. At that point:

1. The placeholder `README.md` will be replaced with a complete model card containing real evaluation results
2. Model weights (safetensors) will be uploaded via Git LFS
3. GGUF quantizations will be uploaded via Git LFS
4. Tokenizer files, config files, and hashes will be added
5. The full release process in `docs/HUGGINGFACE_RELEASE.md` will be followed

**Until then, the repository remains docs-only.**

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [BASE_MODEL_ACCEPTANCE.md](BASE_MODEL_ACCEPTANCE.md) | Pre-release checklist that must be completed before any weights are uploaded |
| [FIRST_PRIVATE_TRAINING_RUN.md](FIRST_PRIVATE_TRAINING_RUN.md) | Private training guide — output stays local, not uploaded |
| [HUGGINGFACE_RELEASE.md](HUGGINGFACE_RELEASE.md) | Full release process for when the transition from placeholder to full release occurs |
| [MODEL_LICENSES.md](../MODEL_LICENSES.md) | License layers documentation |
| [MODEL_DECISION_RECORD.md](MODEL_DECISION_RECORD.md) | ADR-001 — base model candidate comparison |

---

*This plan defines a docs-only placeholder on Hugging Face. No weights, adapters, GGUF files, or fake benchmarks are allowed. The placeholder signals intent without distributing anything. No tokens are committed. No automated uploads exist.*
