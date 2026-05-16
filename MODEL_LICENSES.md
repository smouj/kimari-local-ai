# Model Licensing

This document explains the licensing of models used with Kimari, including base model candidates and private SFT experiments (v0.1.84-alpha).

## Overview

Kimari itself is released under the **MIT License**. However, language model weights carry their own licenses that you must comply with independently. **No Kimari model weights have been released yet.** The final license for any future Kimari model weights will depend on the base model chosen.

## License Layers

### 1. Kimari Software — MIT License

All code in this repository (CLI, scripts, configurations, documentation) is licensed under the MIT License. You are free to use, modify, and distribute the software.

```
Copyright (c) 2025 Smouj
```

### 2. Kimari Fine-Tuning Modifications — MIT License (with base model constraints)

Any fine-tuned models, LoRA adapters, or training recipes produced by the Kimari project are intended to be released under the MIT License. However, when built on a base model with more restrictive terms, the base model's license takes precedence for the combined work. **You cannot apply MIT to derivative weights if the base model forbids it.**

### 3. Base Model Weights — Base Model License

Base model weights are **not** included in this repository. SmolLM3-3B has been accepted for private SFT training, but **not for public release**. Each base model has its own license, which governs how you may use, modify, and redistribute derivative weights.

## Base Model Status (v0.1.84-alpha)

**SmolLM3-3B** has been accepted for private SFT training (v0.1.19-alpha), and a private SFT v2 experiment was completed (150 steps). **It has NOT been accepted for public release.** Public release remains contingent on corrective training passing safety review.

The following candidates remain under evaluation for potential future use:

### SmolLM3 (HuggingFace)

- **License**: Apache 2.0
- **Key properties**: Permissive; permits commercial use, modification, and redistribution with attribution
- **Notes**: Apache 2.0 is the most straightforward path to releasing Kimari weights under a permissive license. However, **verify the license on the specific model card before release** — some SmolLM variants may carry different terms. Always confirm at the HuggingFace model page before relying on Apache 2.0 status.
- **Action required**: Confirm license on the exact SmolLM3 checkpoint before final selection

### Qwen (Alibaba)

- **License**: qwen-research license (visible on HuggingFace model cards)
- **Key properties**: Permits research and non-commercial use; derivative distribution and commercial use may require separate authorization
- **Notes**: The qwen-research license is **not** Apache 2.0. Some earlier Qwen models used different license terms, so always check the specific model card. If a Qwen base is selected, releasing Kimari derivative weights would require reviewing the qwen-research license terms for derivative distribution rights. This may restrict how Kimari weights can be shared.
- **Action required**: Full review of qwen-research license text before any derivative release; determine if commercial redistribution is permitted

### Llama (Meta)

- **License**: Meta Llama Community License Agreement
- **Key properties**: Permits commercial and non-commercial use with restrictions on large-scale distribution (monthly active users threshold); requires compliance with acceptable use policy; includes naming/branding requirements
- **Notes**: The Meta Community License has specific compliance obligations:
  - **User threshold**: Commercial use exceeding 700 million monthly active users requires a separate Meta license
  - **Acceptable use policy**: Must comply with Meta's prohibited uses list
  - **Naming considerations**: Derivative models must follow Meta's naming guidelines (e.g., prefixing with "Llama" or following their specified format)
  - **Redistribution**: Permitted with license inclusion and attribution
- **Action required**: Review latest Meta Llama Community License version; ensure naming and use policy compliance for any derivative

### Summary Table

| Candidate | License | Commercial use | Derivative redistribution | Key consideration |
|-----------|---------|---------------|---------------------------|-------------------|
| SmolLM3 | Apache 2.0 (verify) | ✅ Permitted | ✅ Permitted with attribution | Used for private SFT v2; public release pending safety review |
| Qwen | qwen-research | ⚠️ Restricted | ⚠️ Review required | Not Apache 2.0; research-oriented |
| Llama | Meta Community License | ✅ With limits | ✅ With compliance | User thresholds, naming, use policy |

> **Important**: This table is for evaluation purposes only. It does not constitute legal advice. Always read the original license text.

## No Public Weights Released

As of v0.1.84-alpha, **no Kimari model weights have been publicly released**. Private training experiments (SmolLM3-3B SFT v2) have been conducted, but safety regressions were found during manual review. **No public safetensors, GGUF, or benchmark claims exist.** The license that will apply to any future public Kimari weights depends on successful completion of corrective training, safety review, and license verification before release.

## Dataset Redistribution

**Do not redistribute training datasets unless their licenses explicitly allow it.** Many commonly used datasets have restrictions on redistribution, even when they permit use for training. Before sharing or bundling any dataset:

1. Check the dataset's license on its source page (e.g., HuggingFace, GitHub)
2. Look for specific redistribution clauses — "open" does not always mean "redistributable"
3. When in doubt, link to the original source rather than re-hosting

## Decision Framework: How the Final License Is Determined

The license for Kimari model weights is determined by this process:

1. **Select a base model** — The project evaluates candidates based on quality, size, hardware requirements, and license compatibility
2. **Read the base model's license** — The full license text of the chosen base model governs derivative works
3. **Determine what the base license permits** — Can derivative weights be redistributed? Under what terms? Is commercial use allowed?
4. **Apply the most restrictive applicable terms** — The Kimari project cannot grant rights that the base model license does not permit
5. **Document the final license** — Once a base model is selected, this document will be updated with the definitive license for Kimari weights
6. **Verify before every release** — Licenses can change or specific checkpoints may differ; always re-verify
7. **Safety gate requirement** — No public safetensors or GGUF release is permitted until manual review passes without safety regressions (see `docs/KIMARI4B_RELEASE_GATE.md`)

### Decision flowchart

```
Select base model
       │
       ▼
Read base model license
       │
       ├── Permissive (Apache 2.0, MIT, etc.)
       │       │
       │       ▼
       │   Kimari weights can be released
       │   under permissive terms
       │
       ├── Research / Non-commercial
       │       │
       │       ▼
       │   Kimari weights restricted to
       │   same terms — no commercial
       │   redistribution without authorization
       │
       └── Community license (Meta, etc.)
               │
               ▼
           Kimari weights permitted with
           compliance (naming, use policy,
           user thresholds)
```

## Your Responsibilities

As a user of Kimari, you are responsible for:

1. **Downloading models legally** — Obtain model weights from authorized sources only
2. **Complying with base model licenses** — Read and follow the license of any model you use
3. **Not redistributing restricted weights** — Some licenses prohibit redistribution; do not share weights unless the license allows it
4. **Commercial use compliance** — Check if the base model license permits your intended use
5. **Attribution** — Provide required attribution per the base model's terms
6. **License verification** — Do not assume license terms from summaries; always read the original license text
7. **Dataset compliance** — Do not redistribute training datasets unless their licenses explicitly permit it

## Disclaimer

The Kimari project (created by Smouj) does not host, distribute, or take responsibility for model weights. We provide the software infrastructure to run GGUF-quantized models locally. The end user is solely responsible for ensuring compliance with all applicable model licenses.

The candidate license information above is provided for evaluation purposes and does not constitute legal advice. License terms may vary between specific model versions or checkpoints. Always verify the license on the exact model artifact you intend to use.

## Questions?

If you have questions about model licensing:

1. Read the model card of the specific model you're using
2. Check the license file included with the model weights
3. Consult the model provider's website
4. Seek legal advice if unsure about commercial use

---

*This document is provided for informational purposes only and does not constitute legal advice.*
